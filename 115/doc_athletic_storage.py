"""Persistenz für Modul 115. Fachliche Trainingsverläufe bleiben im Kader erhalten."""
from contextlib import closing, contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3

MAX_STATE_BYTES = 50_000_000
MAX_IMPORT_BYTES = 200_000_000
HISTORY_LIMIT = 100  # Nur technische vollständige Sicherungsstände.
MAX_HISTORY_BYTES = 50_000_000


class StorageConflict(RuntimeError):
    pass


class StorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StorageConfig:
    database_url: str
    data_dir: Path
    db_file: Path
    legacy_file: Path


def encode_state(data):
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(payload.encode("utf-8")) > MAX_STATE_BYTES:
        raise StorageError("Der Kader überschreitet 50 MB. Vor weiteren Änderungen den Datenbestand prüfen.")
    return payload


def decode_backup(raw, validate):
    if len(raw) > MAX_IMPORT_BYTES:
        raise ValueError("Die Importdatei überschreitet 200 MB.")
    data = json.loads(raw)
    encode_state(validate(data))
    # Den ursprünglichen Bereichsumfang erhalten: ein reines Fußball-Backup
    # darf einen nicht enthaltenen Altbestand nicht durch eine leere Liste ersetzen.
    return data


@contextmanager
def remote_connection(url):
    try:
        import psycopg
    except ImportError as exc:
        raise StorageError("Für die externe Datenbank fehlt psycopg.") from exc
    try:
        with psycopg.connect(url, connect_timeout=10) as con:
            yield con
    except psycopg.Error as exc:
        raise StorageError("Externe Datenbank nicht erreichbar. Es wurde kein lokaler Ersatzstand angelegt.") from exc


def load_state(config, default, validate):
    if config.database_url:
        with remote_connection(config.database_url) as con:
            con.execute("CREATE TABLE IF NOT EXISTS doc_athletic_state (id INTEGER PRIMARY KEY CHECK(id=1), revision BIGINT NOT NULL, payload TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS doc_athletic_history (revision BIGINT PRIMARY KEY, payload TEXT NOT NULL, saved_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)")
            con.execute("INSERT INTO doc_athletic_state VALUES (1,0,%s) ON CONFLICT (id) DO NOTHING", (encode_state(validate(default)),))
            row = con.execute("SELECT payload,revision FROM doc_athletic_state WHERE id=1").fetchone()
    else:
        config.data_dir.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(config.db_file, timeout=10)) as con, con:
            con.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, payload TEXT NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS history (revision INTEGER PRIMARY KEY, payload TEXT NOT NULL, saved_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            row = con.execute("SELECT payload,revision FROM state WHERE id=1").fetchone()
            if row is None:
                # Recheck under a write lock before initialization or legacy import.
                con.execute("BEGIN IMMEDIATE")
                row = con.execute("SELECT payload,revision FROM state WHERE id=1").fetchone()
                if row is None:
                    initial = json.loads(config.legacy_file.read_text(encoding="utf-8")) if config.legacy_file.exists() else default
                    payload = encode_state(validate(initial))
                    con.execute("INSERT INTO state VALUES (1,0,?)", (payload,))
                    row = (payload, 0)
    return validate(json.loads(row[0])), row[1]


def save_state(config, data, expected_revision, validate):
    validated = validate(data)
    payload = encode_state(validated)
    if config.database_url:
        with remote_connection(config.database_url) as con:
            old = con.execute("SELECT revision,payload FROM doc_athletic_state WHERE id=1 FOR UPDATE").fetchone()
            _check_revision(old, expected_revision)
            if json.loads(old[1]) == validated:
                return expected_revision
            con.execute("INSERT INTO doc_athletic_history(revision,payload) VALUES (%s,%s) ON CONFLICT (revision) DO NOTHING", old)
            con.execute("UPDATE doc_athletic_state SET payload=%s,revision=revision+1 WHERE id=1", (payload,))
            _prune_history(con, remote=True)
    else:
        with closing(sqlite3.connect(config.db_file, timeout=10)) as con, con:
            con.execute("BEGIN IMMEDIATE")
            old = con.execute("SELECT revision,payload FROM state WHERE id=1").fetchone()
            _check_revision(old, expected_revision)
            if json.loads(old[1]) == validated:
                return expected_revision
            con.execute("INSERT OR IGNORE INTO history(revision,payload) VALUES (?,?)", old)
            con.execute("UPDATE state SET payload=?,revision=revision+1 WHERE id=1", (payload,))
            _prune_history(con, remote=False)
    return expected_revision + 1


def _prune_history(con, remote):
    table = "doc_athletic_history" if remote else "history"
    byte_length = "octet_length(payload)" if remote else "length(CAST(payload AS BLOB))"
    marker = "%s" if remote else "?"
    # Read only revision numbers and sizes; never load the historical payloads.
    rows = con.execute(
        f"SELECT revision,{byte_length} FROM {table} ORDER BY revision DESC LIMIT {marker}",
        (HISTORY_LIMIT + 1,),
    ).fetchall()
    total = 0
    for position, (revision, size) in enumerate(rows):
        total += size
        if position >= HISTORY_LIMIT or total > MAX_HISTORY_BYTES:
            con.execute(f"DELETE FROM {table} WHERE revision <= {marker}", (revision,))
            break


def _check_revision(old, expected_revision):
    if old is None or old[0] != expected_revision:
        raise StorageConflict("Eine andere Sitzung hat inzwischen gespeichert. Bitte den gespeicherten Stand neu laden und Änderungen erneut prüfen.")


def export_backup(config, default, validate):
    data, _ = load_state(config, default, validate)
    # Identisches Format und identische Größe wie beim Speichern.
    return encode_state(data).encode("utf-8")
