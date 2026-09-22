# ============================================================================
# DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE - FUSSBALL & LEICHTATHLETIK (Version 105)
# ChatGPT überarbeitet auf Grundlage 23.8.5; Modul 1
# Überarbeitet: Soll/Ist, 25 Quellenpläne, Folgeempfehlungen, Makrozyklen, Sprungtest-Verlauf
# ============================================================================

import streamlit as st
import pandas as pd
import os
import json
import sqlite3
import math
from pathlib import Path
from copy import deepcopy
from html import escape
import hashlib
import hmac
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from contextlib import contextmanager, closing

st.set_page_config(page_title="Doc Athletic – Modul 1 · 105", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background-color: #000000; color: #ffffff; }
h1, h2, h3, h4, h5, h6, p, label { color: #ffffff !important; }
button[title="View fullscreen"] { display: none !important; }

/* Lesbare aufklappbare Überschriften in allen Bedienzuständen */
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] details > summary:focus,
[data-testid="stExpander"] details > summary:active {
    background-color: #17191c !important;
    color: #ffffff !important;
}
[data-testid="stExpander"] details > summary * {
    color: #ffffff !important;
}
[data-testid="stExpander"] details > summary:focus-visible {
    outline: 2px solid #66fcf1 !important;
    outline-offset: -2px;
}

/* Eingabefelder */
.stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Buttons */
.stButton>button {
    background-color: #1f2833; color: #66fcf1;
    border: 2px solid #45a29e; border-radius: 8px;
    width: 100%; font-weight: bold;
}
div.stDownloadButton > button {
    background-color: #66fcf1 !important;
    border: 2px solid #45a29e !important;
    border-radius: 8px !important;
    width: 100% !important;
    padding: 12px !important;
}
div.stDownloadButton > button *,
div.stDownloadButton > button p,
div.stDownloadButton > button span {
    color: #000000 !important;
    font-weight: 900 !important;
    font-size: 15px !important;
}


/* 103: explizite Kontraste auch für Notizen, Formularbuttons und Sidebar. */
[data-testid="stSidebar"] { background-color: #17191c !important; color: #ffffff !important; }
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    caret-color: #111111 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-baseweb="popover"] [role="option"] {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}
[data-baseweb="popover"] [role="listbox"] { background-color: #ffffff !important; }
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button {
    background-color: #1f2833 !important;
    color: #ffffff !important;
    border: 2px solid #45a29e !important;
}
[data-testid="stButton"] button *,
[data-testid="stFormSubmitButton"] button * { color: #ffffff !important; }
[data-testid="stButton"] button:focus-visible,
[data-testid="stFormSubmitButton"] button:focus-visible { outline: 3px solid #66fcf1 !important; }

/* Steuerungs-Panel */
.steuermatrix {
    background: linear-gradient(145deg, #10161d, #07090c);
    border: 2px solid #66fcf1;
    box-shadow: 0 0 25px rgba(102, 252, 241, 0.25);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 25px;
}

/* Zentrierte und vergrößerte Sportarten-Wahl */
div[role="radiogroup"] {
    justify-content: center !important;
    gap: 30px !important;
    margin: 15px 0 !important;
}
div[role="radiogroup"] label {
    background-color: #1f2833 !important;
    padding: 12px 28px !important;
    border-radius: 10px !important;
    border: 2px solid #45a29e !important;
    cursor: pointer !important;
    transition: all 0.25s ease-in-out !important;
}
div[role="radiogroup"] label:hover {
    border-color: #66fcf1 !important;
    box-shadow: 0 0 15px rgba(102, 252, 241, 0.4) !important;
}
div[role="radiogroup"] label p {
    font-size: 22px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: 0.5px !important;
}

.badge-fussball { 
    background-color: #2ecc71; color: #000000; padding: 8px 18px;
    border-radius: 6px; font-weight: 900; font-size: 16px; display: inline-block;
    box-shadow: 0 0 10px rgba(46, 204, 113, 0.4);
}
.badge-leichtathletik { 
    background-color: #e74c3c; color: #ffffff; padding: 8px 18px;
    border-radius: 6px; font-weight: 900; font-size: 16px; display: inline-block;
    box-shadow: 0 0 10px rgba(231, 76, 60, 0.4);
}

.footer-box {
    text-align: center; border: 2px solid #66fcf1; border-radius: 10px;
    padding: 25px; margin-top: 40px; margin-bottom: 20px; background-color: #0b0c10;
}

@media print {
    @page { size: landscape; margin: 10mm; }
    body { background-color: #ffffff !important; color: #000000 !important; }
    .stApp, .steuermatrix, .footer-box { background-color: #ffffff !important; color: #000000 !important; border: none !important; }
    h1, h2, h3, h4, h5, h6, p, label, span { color: #000000 !important; }
    .stButton, .stDownloadButton, [data-testid="stSidebar"], .stRadio { display: none !important; }
    .druck-block { background-color: #ffffff !important; color: #000000 !important; border: none !important; }
}
</style>
""", unsafe_allow_html=True)

def lade_bild(dateinamen_liste, use_col=False):
    for name in dateinamen_liste:
        if os.path.exists(name):
            if use_col:
                st.image(name, use_container_width=True)
            return True
    return False

def setting(name):
    value = os.environ.get(name)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(name, ""))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ""

TRAINER_CODE = setting("DOC_ATHLETIC_TRAINER_CODE")
GAST_CODE = setting("DOC_ATHLETIC_GAST_CODE")
DATABASE_URL = setting("DOC_ATHLETIC_DATABASE_URL")
if TRAINER_CODE and GAST_CODE and TRAINER_CODE == GAST_CODE:
    st.error("Trainer- und Gastcode müssen unterschiedlich sein.")
    st.stop()

# SQLite writes are transactional; revisions prevent stale sessions overwriting data.
# The hosting platform must retain this directory. JSON downloads are portable backups.
DATA_DIR = Path(os.environ.get("DOC_ATHLETIC_DATA_DIR", str(Path(__file__).resolve().parent)))
DB_FILE = DATA_DIR / "doc_athletic.sqlite3"
KADER_DATEI = DATA_DIR / "kader_db.json"
VALID_PROFILES = {'Fussball_U13', 'Leichtathletik_MASTER_w', 'Fussball_U23_m', 'Fussball_U23_w', 'Fussball_MASTER_w', 'Fussball_U20_m', 'Leichtathletik_MASTER_m', 'Leichtathletik_U17_m', 'Fussball_U17_w', 'Fussball_U15_w', 'Leichtathletik_U11', 'Leichtathletik_U15', 'Leichtathletik_U17_w', 'Leichtathletik_U20_w', 'Fussball_U15_m', 'Fussball_U17_m', 'Fussball_U20_w', 'Leichtathletik_U23_w', 'Fussball_MASTER_m', 'Leichtathletik_U20_m', 'Leichtathletik_U13', 'Leichtathletik_U23_m', 'Fussball_U11'}
DEFAULT_KADER = {"Fussball": {}, "Leichtathletik": {}}


class StorageConflict(Exception):
    pass

TEMPO_DISTANCES = [50, 60, 75, 100, 150, 200] + list(range(250, 801, 50))
TEMPO_PERCENTAGES = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50]

def format_tempo_time(seconds):
    # Round once before splitting, so 59.96 seconds becomes 1:00.0.
    tenths = round(seconds * 10)
    if tenths >= 600:
        minutes, rest = divmod(tenths, 600)
        return f"{minutes}:{rest / 10:04.1f} min"
    return f"{tenths / 10:.1f} s"

def estimate_time(distance, anchors, extrapolate):
    points = sorted((int(d), float(t)) for d,t in anchors.items() if t > 0)
    if len(points) < 2:
        return None
    left = [p for p in points if p[0] < distance]
    right = [p for p in points if p[0] > distance]
    if left and right:
        (d1,t1),(d2,t2) = left[-1],right[0]
        source = "Richtwert zwischen Referenzen"
    elif extrapolate and left and distance > points[-1][0] and points[-1][0] >= 300 and distance <= min(800,2*points[-1][0]):
        (d1,t1),(d2,t2) = points[-2:]
        source = "Richtwert über längste Referenz hinaus"
    else:
        return None
    if t2 <= t1:
        return None
    exponent = math.log(t2/t1) / math.log(d2/d1)
    return t1 * (distance/d1)**exponent, source

def build_tempo_table(t60, t150, source150, references, test_distance, test_seconds, interpolate=True, extrapolate=False):
    calc100 = round(t60 * 1.615, 2)
    modeled = {50:calc100 / 1.93, 75:calc100 * .775, 100:calc100,
               150:t150, 200:round(t60 * 3.265,2)}
    anchors = {60:t60}
    if source150 != "berechnet":
        anchors[150] = t150
    if test_seconds > 0:
        anchors[test_distance] = test_seconds
    anchors.update({int(d):t for d,t in references.items() if t > 0})
    result = []
    for distance in TEMPO_DISTANCES:
        explicit = references.get(str(distance), 0)
        estimation = estimate_time(distance,anchors,extrapolate) if interpolate else None
        if explicit > 0:
            base, source = explicit, "Trainerreferenz"
        elif distance == test_distance and test_seconds > 0:
            base, source = test_seconds, "Referenz: Einzeltest"
        elif distance == 60:
            base, source = t60, "60-m-Referenz"
        elif distance == 150 and source150 != "berechnet":
            base, source = t150, "150-m-Referenz"
        elif estimation is not None:
            base,source = estimation
        elif distance in modeled:
            base,source = modeled[distance], "Richtwert aus Kurzsprint"
        else:
            base,source = None, "Längere Referenz ergänzen"
        row = {"Distanz":f"{distance}m", "Herkunft":source}
        for percent in TEMPO_PERCENTAGES:
            seconds = base / (percent / 100) if base is not None else None
            # Longer training runs use whole seconds; inputs retain their precision.
            if seconds is None:
                value = "—"
            elif distance >= 250:
                total = round(seconds)
                minutes, rest = divmod(total,60)
                value = f"{minutes}:{rest:02d} min" if minutes else f"{total} s"
            else:
                value = format_tempo_time(seconds)
            row[f"{percent}%"] = value
        result.append(row)
    return result

JUMP_TESTS = {"hop_links": "Fünfer-Hop links", "hop_rechts": "Fünfer-Hop rechts", "schluss": "Fünfer-Schlusssprung"}

def jump_summary(test):
    best = {key: max(test[key], default=0) for key in JUMP_TESTS}
    left, right = best["hop_links"], best["hop_rechts"]
    both = left > 0 and right > 0
    return {"Testdatum": test["datum"],
        "Hop links (m)": left or None, "Hop rechts (m)": right or None,
        "Schlusssprung (m)": best["schluss"] or None,
        "Differenz (cm)": round(abs(left-right)*100, 1) if both else None,
        "Abweichung (%)": round(abs(left-right)/((left+right)/2)*100, 2) if both else None,
        "Größere Weite": ("gleich" if left == right else "links" if left > right else "rechts") if both else "noch offen",
        "Techniknotizen": test["notizen"]}

def validate_jump_tests(tests):
    if not isinstance(tests, list) or len(tests) > 10000:
        raise ValueError("Ungültiger Sprungtest-Verlauf.")
    for test in tests:
        if not isinstance(test, dict):
            raise ValueError("Ungültiger Sprungtest.")
        try:
            date.fromisoformat(test.get("datum", ""))
        except (ValueError, TypeError):
            raise ValueError("Ungültiges Testdatum.") from None
        if not isinstance(test.get("notizen"), str) or len(test["notizen"]) > 4000:
            raise ValueError("Ungültige Techniknotizen.")
        for key in JUMP_TESTS:
            values = test.get(key)
            if not isinstance(values, list) or len(values) != 3 or any(
                type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100 for v in values):
                raise ValueError("Je Sprungtest sind drei Weiten zwischen 0 und 100 Metern erforderlich; 0 bedeutet nicht gewertet.")
        if not any(v > 0 for key in JUMP_TESTS for v in test[key]):
            raise ValueError("Mindestens eine gültige Sprungweite eintragen.")

SOURCE_UNITS = {}  # Private Originalpläne werden bei Bedarf vom Trainer geladen.

# Soll und Ist werden unabhängig voneinander versioniert gespeichert.
PROTOCOL_COLUMNS = ["Übung", "Last (kg)", "Sätze", "Wdh. je Satz/Seite", "Strecke (m)", "Zeit (s)", "Technik", "Belastung", "Anmerkung"]
NUMERIC_COLUMNS = PROTOCOL_COLUMNS[1:6]

# Shared source embedded in each standalone main.py at build time.
WEEK_RULES_VERSION = '2026-09-20-wochensteuerung'

def validate_timing(timing):
    if not isinstance(timing, dict):
        raise ValueError('Ungültige Zeitplanung.')
    fields = ('planned_athletic_min', 'actual_athletic_min', 'planned_transfer_min', 'actual_transfer_min')
    for field in fields:
        value = timing.get(field)
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1440):
            raise ValueError('Dauer muss eine endliche, nicht negative Minutenzahl sein.')
    for key in ('athletic_hint', 'transfer_hint', 'model'):
        if key in timing and (not isinstance(timing[key], str) or len(timing[key]) > 1500):
            raise ValueError('Ungültiger Hinweis zur Zeitplanung.')
    return deepcopy(timing)

def validate_organization(config):
    if not isinstance(config, dict):
        raise ValueError('Ungültige Blockorganisation.')
    for key, low, high in [('group_size', 3, 5), ('main_sets', 4, 5), ('gap_days', 1, 7)]:
        value = config.get(key, {'group_size': 4, 'main_sets': 4, 'gap_days': 3}[key])
        if type(value) is not int or not low <= value <= high:
            raise ValueError('Ungültige Blockorganisation: ' + key)
    return deepcopy(config)

def effective_unit(frequency, unit):
    # A single session always contains the combined programme, even with an old TE2 selection.
    if frequency not in (1, 2):
        raise ValueError('Eine oder zwei zusätzliche Athletikeinheiten auswählen.')
    return 'Basis' if frequency == 1 else ('TE2' if unit == 'TE2' else 'TE1')

def weekly_timing(sport, band, frequency, unit):
    unit = effective_unit(frequency, unit)
    timing = dict(planned_athletic_min=None, planned_transfer_min=None,
                  actual_athletic_min=None, actual_transfer_min=None)
    timing['model'] = ('1 zusätzliche Athletikeinheit pro Woche: vollständiges Komplextraining'
                       if frequency == 1 else '2 zusätzliche Athletikeinheiten pro Woche: ' +
                       ('Haupteinheit' if unit == 'TE1' else 'kürzere zweite Einheit'))
    timing['athletic_hint'] = 'Dauer nach vollständigem Einheitsplan; Erwärmung eingeschlossen.'
    timing['transfer_hint'] = 'Sportartspezifischer Anschluss wird separat geplant.'
    if frequency == 2 and sport != 'Skispringen':
        main = {'U11': (60, 60), 'U13': (70, 70), 'U15': (75, 75), 'U17': (75, 75)}
        second = {'U11': (35, 35), 'U13': (40, 40), 'U15': (45, 45), 'U17': (45, 45)}
        low, high = (main.get(band, (80, 90)) if unit == 'TE1' else second.get(band, (50, 60)))
        timing['planned_athletic_min'] = float(low)
        label = str(low) if low == high else f'{low}–{high}'
        timing['athletic_hint'] = f'Richtwert {label} Minuten einschließlich Erwärmung; individuell veränderbar.'
        if sport in ('Fussball', 'Basketball'):
            timing['planned_transfer_min'] = 30.
            timing['transfer_hint'] = ('Fußballspezifischer Anschluss: Richtwert 30–45 Minuten zusätzlich.'
                                       if sport == 'Fussball' else
                                       'Basketballspezifischer Anschluss: Vorschlag 30–45 Minuten zusätzlich.')
    if sport == 'Leichtathletik':
        timing['transfer_hint'] = 'Anschluss beispielsweise lockere Steigerungsläufe; keine pauschale Zusatzdauer.'
    if sport == 'Skispringen':
        timing['athletic_hint'] = 'Sportartspezifische Dauer einschließlich Erwärmung eintragen.'
        timing['transfer_hint'] = 'Skisprungspezifischer Transfer im eigenen Ablauf; kein pauschaler Ballteil.'
    return timing

def organization_text(frequency, config=None):
    config = validate_organization(config or {})
    size = config.get('group_size', 4)
    text = (f'Blocktraining in Minigruppen von {size} Personen mit vergleichbaren Voraussetzungen. '
            'Die Übungen eines Blocks nacheinander absolvieren; Stationswechsel bis 60 s. '
            'Anschließend der zugehörige Lauf- oder Techniktransfer. Serien- und Laufpausen bleiben separat. ')
    if frequency == 1:
        text += 'Eine vollständige Einheit mit den vorgesehenen Kraft-, Koordinations- und Schnelligkeitsanteilen.'
    else:
        text += (f'Haupteinheit mit {config.get("main_sets", 4)} Sätzen an den Kraftstationen; '
                 f'kürzere zweite Einheit mit Schwerpunkt Schnelligkeit und Reaktivität. '
                 f'Planungsabstand: {config.get("gap_days", 3)} Tage zwischen den Einheiten. '
                 'Erwärmung und ihre integrierten Beschleunigungs- und Technikanteile bleiben in beiden Einheiten.')
    return text + ' Qualität und Belastungsverträglichkeit bestimmen den Ablauf; Zeiten sind Richtwerte.'

def organization_ui(saved, frequency, key, disabled=False):
    config = deepcopy(saved or {})
    st.caption('Standard: eine zusätzliche Athletikeinheit pro Woche neben dem Sporttraining. Die Aufteilung greift erst bei zwei gewählten Einheiten.')
    config['group_size'] = st.number_input('Personen je Minigruppe', 3, 5, int(config.get('group_size', 4)), key=key+'group', disabled=disabled)
    if frequency == 2:
        config['main_sets'] = st.number_input('Sätze an Kraftstationen der Haupteinheit', 4, 5, int(config.get('main_sets', 4)), key=key+'sets', disabled=disabled)
        config['gap_days'] = st.number_input('Tage zwischen den beiden Athletikeinheiten', 1, 7, int(config.get('gap_days', 3)), key=key+'gap', disabled=disabled)
    st.caption(organization_text(frequency, config))
    return config

def timing_plan_ui(defaults, saved, key, disabled=False):
    timing = deepcopy(saved if saved is not None else defaults)
    st.caption(timing.get('model', defaults.get('model', '')))
    st.caption(timing.get('athletic_hint', defaults.get('athletic_hint', '')))
    st.caption(timing.get('transfer_hint', defaults.get('transfer_hint', '')))
    st.caption('Minuten sind flexible Richtwerte. Einige Minuten mehr oder weniger führen zu keiner Kürzung oder Sperre. Ein leeres Feld bedeutet: noch nicht erfasst.')
    timing['planned_athletic_min'] = st.number_input('Soll: Athletik einschließlich Erwärmung (min)', min_value=0., max_value=1440., value=timing.get('planned_athletic_min'), step=1., key=key+'planned_athletic', disabled=disabled)
    timing['planned_transfer_min'] = st.number_input('Soll: sportartspezifischer Anschluss zusätzlich (min)', min_value=0., max_value=1440., value=timing.get('planned_transfer_min'), step=1., key=key+'planned_transfer', disabled=disabled)
    return timing

def timing_actual_ui(saved, key, disabled=False):
    timing = deepcopy(saved or {})
    timing['actual_athletic_min'] = st.number_input('Ist: Athletik einschließlich Erwärmung (min)', min_value=0., max_value=1440., value=timing.get('actual_athletic_min'), step=1., key=key+'actual_athletic', disabled=disabled)
    timing['actual_transfer_min'] = st.number_input('Ist: sportartspezifischer Anschluss zusätzlich (min)', min_value=0., max_value=1440., value=timing.get('actual_transfer_min'), step=1., key=key+'actual_transfer', disabled=disabled)
    return timing

def timing_html(timing):
    timing = validate_timing(timing or {})
    def cell(value):
        return 'nicht erfasst' if value is None else f'{value:g} min'
    rows = []
    for label, suffix in [('Athletik einschließlich Erwärmung', 'athletic_min'), ('Sportartspezifischer Anschluss zusätzlich', 'transfer_min')]:
        planned, actual = timing.get('planned_'+suffix), timing.get('actual_'+suffix)
        difference = '—' if planned is None or actual is None else f'{actual-planned:+g} min'
        rows.append('<tr>' + ''.join('<td>'+escape(x)+'</td>' for x in [label, cell(planned), cell(actual), difference]) + '</tr>')
    return ('<h3>Zeitplanung und Durchführung</h3><p>'+escape(timing.get('model', ''))+'</p>'
            '<p>'+escape(timing.get('athletic_hint', ''))+' '+escape(timing.get('transfer_hint', ''))+'</p>'
            '<p>Flexible Richtwerte; Qualität und Organisation haben Vorrang. Kein automatischer Abbruch.</p>'
            '<table><thead><tr><th>Abschnitt</th><th>Soll</th><th>Ist</th><th>Abweichung</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')

def recorded_duration(timing):
    return any(timing.get(k) is not None for k in ('actual_athletic_min', 'actual_transfer_min'))

def session_record(record, cycle, te, unit):
    sessions = record.get('einheitenprotokoll', {})
    specific = sessions.get(json.dumps([cycle, te, unit], ensure_ascii=False))
    if specific is not None: return specific
    legacy = sessions.get(json.dumps([cycle, te], ensure_ascii=False))
    if legacy is None: return None
    legacy_unit = legacy.get('unit')
    if legacy_unit is None:
        # Old exports recorded the unit in their heading. Keep unmatched legacy entries
        # intact instead of attaching the same Ist record to two different weekly models.
        for candidate in ('Basis', 'TE1', 'TE2'):
            if f'· {candidate} ·' in legacy.get('plan', ''):
                legacy_unit = candidate
                break
    return legacy if legacy_unit == unit else None


def validate_sessions(sessions):
    if not isinstance(sessions, dict) or len(sessions) > 2000:
        raise ValueError("Ungültiges Einheitenprotokoll.")
    def validate_payload(item):
        if not isinstance(item, dict):
            raise ValueError("Ungültiger Einheitenstand.")
        for k in ("original_plan", "plan", "source", "cycle", "notes", "saved_at"):
            if not isinstance(item.get(k, ""), str) or len(item.get(k, "")) > 100000:
                raise ValueError("Ungültiger Text im Einheitenprotokoll.")
        if type(item.get("te")) is not int or not 1 <= item["te"] <= 28:
            raise ValueError("Ungültige Einheitsnummer.")
        if "performed" in item:
            try:
                date.fromisoformat(item["performed"])
            except (ValueError, TypeError):
                raise ValueError("Ungültiges Durchführungsdatum.") from None
        validate_timing(item.get("timing", {}))
        rows = item.get("actual", [])
        if not isinstance(rows, list) or len(rows) > 150:
            raise ValueError("Ungültige Ist-Tabelle.")
        for row in rows:
            if not isinstance(row, dict) or set(row) != set(PROTOCOL_COLUMNS):
                raise ValueError("Ungültige Ist-Zeile.")
            if not isinstance(row["Übung"], str) or not row["Übung"].strip() or len(row["Übung"]) > 300:
                raise ValueError("Jede Ist-Zeile benötigt einen Übungsnamen.")
            for key in NUMERIC_COLUMNS:
                val = row[key]
                if val is not None and (type(val) not in (int, float) or not math.isfinite(val) or not 0 <= val <= 100000):
                    raise ValueError(f"Ungültiger Ist-Wert: {key}.")
            for key in ("Sätze", "Wdh. je Satz/Seite"):
                if row[key] is not None and int(row[key]) != row[key]:
                    raise ValueError("Sätze und Wiederholungen müssen ganze Zahlen sein.")
            if row["Technik"] not in ("Nicht bewertet", "Sauber", "Unsicher") or row["Belastung"] not in ("Nicht bewertet", "Gut bewältigt", "Grenzwertig", "Nicht bewältigt"):
                raise ValueError("Ungültige Rückmeldung.")
            if not isinstance(row["Anmerkung"], str) or len(row["Anmerkung"]) > 4000:
                raise ValueError("Ungültige Ist-Anmerkung.")
    for key, item in sessions.items():
        if not isinstance(key, str) or len(key) > 300:
            raise ValueError("Ungültiger Einheitenschlüssel.")
        validate_payload(item)
        revisions = item.get("revisions", [])
        if not isinstance(revisions, list) or len(revisions) > 200:
            raise ValueError("Zu viele Korrekturen für diese Einheit.")
        for old in revisions:
            if "revisions" in old:
                raise ValueError("Verschachtelte Korrekturhistorie ist ungültig.")
            validate_payload(old)

def save_unit_record(record, cycle, te, plan, source, actual=None, notes=None, performed=None, timing=None):
    updated = deepcopy(record)
    sessions = updated.setdefault("einheitenprotokoll", {})
    key = json.dumps([cycle, te], ensure_ascii=False)
    old = sessions.get(key)
    history = deepcopy(old.get("revisions", [])) if old else []
    if old:
        previous = deepcopy(old)
        previous.pop("revisions", None)
        history.append(previous)
    item = deepcopy(old) if old else {"cycle": cycle, "te": te, "original_plan": plan, "actual": [], "notes": ""}
    item.update(plan=plan, source=source, saved_at=datetime.now(timezone.utc).isoformat(), revisions=history)
    if actual is not None:
        item["actual"] = deepcopy(actual)
    if notes is not None:
        item["notes"] = notes
    if performed is not None:
        date.fromisoformat(performed)
        item["performed"] = performed
    if timing is not None:
        item["timing"] = validate_timing(timing)
    sessions[key] = item
    validate_sessions(sessions)
    return updated

def next_recommendations(record, cycle, te, metric, percent):
    # Zeitangaben sind ausdrücklich keine Last-/Wiederholungsprogression.
    if metric not in ("Last (kg)", "Wdh. je Satz/Seite", "Strecke (m)") or not 0 <= percent <= 20:
        raise ValueError("Ungültige Steigerungseinstellung.")
    latest = {}
    entries = sorted(record.get("einheitenprotokoll", {}).values(), key=lambda x: (x.get("performed", ""), x.get("saved_at", "")))
    for item in entries:
        if item["cycle"] == cycle and item["te"] >= te:
            continue
        grouped = {}
        for row in item.get("actual", []):
            identity = row["Übung"].strip().casefold()
            grouped.setdefault(identity, []).append(row)
        for identity, rows in grouped.items():
            candidates = [r for r in rows if r[metric] is not None and r[metric] > 0]
            if not candidates:
                continue
            combined = deepcopy(min(candidates, key=lambda r: r[metric]))
            combined["Technik"] = "Unsicher" if any(r["Technik"] == "Unsicher" for r in rows) else "Sauber" if all(r["Technik"] == "Sauber" for r in rows) else "Nicht bewertet"
            combined["Belastung"] = "Nicht bewältigt" if any(r["Belastung"] == "Nicht bewältigt" for r in rows) else "Grenzwertig" if any(r["Belastung"] == "Grenzwertig" for r in rows) else "Gut bewältigt" if all(r["Belastung"] == "Gut bewältigt" for r in rows) else "Nicht bewertet"
            latest[identity] = (combined, item)
    output = []
    for row, item in latest.values():
        value = row[metric]
        if value is None or value <= 0:
            continue
        good = row["Technik"] == "Sauber" and row["Belastung"] == "Gut bewältigt"
        bad = row["Technik"] == "Unsicher" or row["Belastung"] in ("Grenzwertig", "Nicht bewältigt")
        factor = -percent if bad else percent if good else 0
        target = value * (1 + factor / 100)
        if metric == "Wdh. je Satz/Seite":
            target = max(1, math.floor(target))
        else:
            target = round(target, 2)
        reason = "Reduktionsvorschlag aus Rückmeldung" if bad else "Steigerungsvorschlag aus Rückmeldung" if good else "Beibehalten; Rückmeldung unvollständig"
        if percent == 0:
            reason = "Beibehalten; Änderungsrate 0 %"
        effective = (target/value-1)*100
        output.append({"Übung":row["Übung"], "Ausgangswert":value, "Parameter":metric, "Empfehlung":target,
                       "Änderung tatsächlich (%)":round(effective,2), "Begründung":reason,
                       "Quelle":f'{item["cycle"]}, TE {item["te"]}'})
    return output

class PlanTextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag in ("tr", "p", "h3", "br"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.parts.append(" | ")
    def handle_data(self, data):
        self.parts.append(data)

def plan_as_text(html):
    parser=PlanTextParser();parser.feed(html)
    return "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())

def protocol_rows(frame):
    rows=[]
    for row in frame.to_dict("records"):
        if not str(row.get("Übung") or "").strip():
            if all(pd.isna(row.get(k)) for k in NUMERIC_COLUMNS):
                continue
            raise ValueError("Bitte den Übungsnamen zu den eingetragenen Werten ergänzen.")
        clean={k:row.get(k) for k in PROTOCOL_COLUMNS}
        for k in NUMERIC_COLUMNS:
            clean[k]=None if pd.isna(clean[k]) else float(clean[k])
        for k in ("Übung","Anmerkung"):
            clean[k]="" if pd.isna(clean[k]) else str(clean[k]).strip()
        rows.append(clean)
    return rows

def unit_workflow(athlete, sport, target, te, default_plan, key_for, guest, default_timing=None):
    cycle=athlete.get("aktiver_makrozyklus", "Bestand")
    unit_key=json.dumps([cycle,te],ensure_ascii=False)
    saved=athlete.get("einheitenprotokoll",{}).get(unit_key)
    prefix=key_for("protocol_"+hashlib.sha256(unit_key.encode()).hexdigest()[:10])
    st.subheader(f"TE {te}: Plan und tatsächliche Durchführung")
    st.caption("Minigruppen mit vergleichbaren Voraussetzungen. Übungen im Block erhalten; danach das zugehörige Laufprogramm. Stationswechsel höchstens 60 Sekunden. Serien- und Laufpausen bleiben separat.")
    st.caption("Team-Style: etwa 2 Meter Abstand; Führung nach aktueller Leistungsfähigkeit, Wechsel nach Abstimmung.")
    sources=["Generierter Altersklassenplan"]+list(st.session_state.get("private_sources", SOURCE_UNITS))
    if saved and saved["source"] not in sources:
        sources.append(saved["source"])
    source=st.selectbox("Plangrundlage",sources,index=sources.index(saved["source"]) if saved and saved["source"] in sources else 0,key=prefix+"source",disabled=guest)
    initial=default_plan if source==sources[0] else st.session_state.get("private_sources", SOURCE_UNITS).get(source, saved["plan"] if saved else "")
    if saved and source==saved["source"]:
        initial=saved["plan"]
    if source!=sources[0]:
        st.caption("Dokumentierte Einheit für den damaligen Jahrgang. Lasten vor Übernahme an das aktuelle Profil anpassen; Notizen zur damaligen Durchführung sind Quellenangaben.")
    plan=st.text_area("Sollplan: Blöcke, Übungsfolge und Laufprogramm",initial,height=350,max_chars=100000,key=prefix+"plan_"+hashlib.sha256(source.encode()).hexdigest()[:8],disabled=guest)
    metric=st.selectbox("Parameter für Folgeempfehlung",["Wdh. je Satz/Seite","Last (kg)","Strecke (m)"],key=prefix+"metric",disabled=guest)
    pct=st.number_input("Änderungsempfehlung (%)",0.0,20.0,float(athlete.get("folge_rate",0)),0.5,key=prefix+"pct",disabled=guest)
    st.caption("Nur ein Parameter wird vorgeschlagen. Die Rate ist deine Vorgabe, keine automatisch ermittelte Leistungsfähigkeit. 0 % bedeutet beibehalten. Lastvorschläge müssen zum vorhandenen Gerät passen.")
    recs=next_recommendations(athlete,cycle,te,metric,pct)
    if recs:
        st.dataframe(pd.DataFrame(recs),hide_index=True)
        st.caption("Vorschläge gelten nur beim erneuten Einsatz derselben Übung und Ausführung. Bei mehreren Sätzen wird der kleinste positive Ausgangswert und die ungünstigste Rückmeldung berücksichtigt.")
        selected = st.multiselect("Empfehlungen für Übungen dieser Einheit übernehmen",[r["Übung"] for r in recs],key=prefix+"selected",disabled=guest)
        def append_recommendations():
            additions = [f"{r['Übung']}: {r['Parameter']} {r['Ausgangswert']:g} → {r['Empfehlung']:g} ({r['Änderung tatsächlich (%)']:+g} %), {r['Begründung']}; aus {r['Quelle']}" for r in recs if r["Übung"] in selected]
            plan_key = prefix+"plan_"+hashlib.sha256(source.encode()).hexdigest()[:8]
            st.session_state[plan_key] += "\n\nÜbernommene individuelle Anpassungen (ersetzen die entsprechenden Ausgangswerte):\n" + "\n".join(additions)
        st.button("Ausgewählte Empfehlungen in Sollplan ergänzen",key=prefix+"apply",on_click=append_recommendations,disabled=guest or not selected)
    else:
        st.info("Noch keine vorherige Ist-Einheit mit geeigneten Zahlenwerten vorhanden.")
    timing_plan = timing_plan_ui(default_timing or {}, saved.get("timing") if saved else None, prefix+"timing_", guest)
    save_plan=st.button("Sollplan dieser Einheit speichern",key=prefix+"saveplan",disabled=guest)
    if saved:
        with st.expander("Ursprünglicher Sollplan und Korrekturverlauf"):
            st.text(saved["original_plan"])
            for revision in reversed(saved.get("revisions",[])):
                st.write(revision.get("saved_at",""))
                st.text(revision["plan"])
                if revision.get("actual"):
                    st.dataframe(pd.DataFrame(revision["actual"]),hide_index=True)
    initial_rows=saved.get("actual",[]) if saved else []
    if not initial_rows:
        initial_rows=[{"Übung":"",**{k:None for k in NUMERIC_COLUMNS},"Technik":"Nicht bewertet","Belastung":"Nicht bewertet","Anmerkung":""}]
    configs={k:st.column_config.NumberColumn(k,min_value=0,step=1 if k in ("Sätze","Wdh. je Satz/Seite") else 0.1) for k in NUMERIC_COLUMNS}
    configs["Technik"]=st.column_config.SelectboxColumn(options=["Nicht bewertet","Sauber","Unsicher"],required=True)
    configs["Belastung"]=st.column_config.SelectboxColumn(options=["Nicht bewertet","Gut bewältigt","Grenzwertig","Nicht bewältigt"],required=True)
    st.markdown("**Was wurde tatsächlich absolviert?**")
    st.caption("Eine Zeile je Übung/Ausführung. Bei wechselnden Lasten oder Wiederholungen eine Zeile je Satz. Wiederholungen bei Wechselübungen je Seite, Last bei Kurzhanteln je Hand im Übungsnamen kennzeichnen. Leeres Zahlenfeld bedeutet nicht erfasst, 0 ist ein erfasster Wert.")
    actual_frame = pd.DataFrame(initial_rows,columns=PROTOCOL_COLUMNS)
    for column in NUMERIC_COLUMNS:
        actual_frame[column] = pd.to_numeric(actual_frame[column], errors="coerce").astype(float)
    edited=st.data_editor(actual_frame,column_config=configs,num_rows="dynamic",hide_index=True,key=prefix+"actual",disabled=guest)
    performed=st.date_input("Durchgeführt am",date.fromisoformat(saved.get("performed",date.today().isoformat())) if saved else date.today(),key=prefix+"date",disabled=guest)
    notes=st.text_area("Verlauf / Abweichungen vom Plan",saved.get("notes","") if saved else "",key=prefix+"notes",max_chars=4000,disabled=guest)
    timing_actual = timing_actual_ui(saved.get("timing", {}) if saved else {}, prefix+"timing_", guest)
    save_actual=st.button("Ist-Durchführung speichern / korrigieren",key=prefix+"saveactual",disabled=guest or not saved)
    if not saved:
        st.caption("Zuerst den Sollplan speichern, danach die tatsächliche Durchführung erfassen.")
    if save_plan or save_actual:
        try:
            rows=protocol_rows(edited) if save_actual else None
            if save_actual and not rows and not recorded_duration(timing_actual):
                raise ValueError("Mindestens eine absolvierte Übung eintragen.")
            updated=deepcopy(st.session_state.kader_db)
            rec=save_unit_record(updated[sport][target],cycle,te,saved["plan"] if save_actual else plan,saved["source"] if save_actual else source,
                                actual=rows,notes=notes if save_actual else None,performed=performed.isoformat() if save_actual else None, timing=timing_actual if save_actual else timing_plan)
            rec["folge_rate"]=pct
            updated[sport][target]=rec
            revision=speichere_kader_in_datei(updated,st.session_state.kader_revision)
            st.session_state.kader_db=updated;st.session_state.kader_revision=revision
            st.session_state.edit_epoch=st.session_state.get("edit_epoch",0)+1
            st.session_state.save_notice="Sollplan gespeichert." if save_plan else "Ist-Durchführung gespeichert; Folgeempfehlungen stehen bei der nächsten Einheit bereit."
            st.rerun()
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:
            st.error(f"Einheit nicht gespeichert: {exc}")
    if saved:
        report="<!doctype html><html lang='de'><meta charset='utf-8'><title>Einheitenprotokoll</title><style>body{font-family:Arial}pre{white-space:pre-wrap}td,th{border:1px solid #999;padding:5px}table{border-collapse:collapse}</style>"
        report+=f"<h1>{escape(target)} – {escape(cycle)} – TE {te}</h1><h2>Gespeicherter Sollplan</h2><pre>{escape(saved['plan'])}</pre>"
        report+=timing_html(saved.get("timing", {}))
        report+="<h2>Tatsächliche Durchführung</h2>"+pd.DataFrame(saved["actual"],columns=PROTOCOL_COLUMNS).to_html(index=False,escape=True,na_rep="—")
        report+=f"<p>{escape(saved.get('performed',''))}</p><pre>{escape(saved.get('notes',''))}</pre></html>"
        st.download_button("Soll-/Ist-Protokoll herunterladen",report,file_name=f"Modul1_TE{te}_Protokoll.html",mime="text/html",key=prefix+"download")


"""Modul 1 Version 105: explicit coach-defined reference calculation, no telemetry control."""
import math
from datetime import date
POWERBAGS = (5,8,10,12,15,17,20)
RM_BANDS = ('U17','U20','U23','MASTER')
VBT_KINDS = ('Nicht zugeordnet','Mittlere konzentrische Geschwindigkeit','Spitzengeschwindigkeit')

# Doc Athletic: getrennte Ball-Erwärmung und maximale M-Sprints, 20.09.2026.
M_TRAINING_REVISION = '105-205-305-M-Formen'
M_BALL_EDGES = {'U11': 24., 'U13': 26., 'U15': 28.}
E2_BALL_DISTANCES = (70., 75., 80., 85., 90., 95.)
M_MAX_EDGES = {'U11': (10., 15.), 'U13': (12., 18.), 'U15': (15., 20.)}
MACHINE_REFERENCE_NOTE = (
    'Frühere Orientierungsangabe 1,30 m/s: für die neue Maschine noch nicht '
    'kalibriert. Schlittenmasse, Zusatzlast, Rollwiderstand/Reibung, Übungsausführung '
    'und Messverfahren müssen zuerst dokumentiert werden. Bis dahin erfolgt daraus '
    'keine Bewertung als zu langsam oder optimal und keine automatische Laständerung. '
    'Die Sensoranbindung bleibt inaktiv.'
)


def m_training_defaults(sport, band):
    return {
        'sport': sport, 'band': band,
        'ball': {'enabled': sport in ('Fussball', 'Basketball') and band in M_BALL_EDGES,
                 'edge_m': 17.5 if (sport, band) == ('Fussball', 'U11') else M_BALL_EDGES.get(band, 24.),
                 'series': 2 if band == 'U11' else 3, 'runs': 5,
                 'run_seconds': None, 'notes': '',
                 'e2_progression': (sport, band) == ('Fussball', 'U11'),
                 'timed_distance_m': None},
        'maximal': {'enabled': False, 'edge_m': M_MAX_EDGES.get(band, (10., 25.))[0],
                    'series': 3, 'runs': 5, 'run_seconds': None, 'units': [], 'notes': ''},
    }


def validate_m_training(value, sport, band):
    if not isinstance(value, dict):
        raise ValueError('M-Lauf-Vorgaben müssen ein Objekt sein.')
    if value and (value.get('sport', sport) != sport or value.get('band', band) != band):
        raise ValueError('M-Lauf-Vorgaben gehören zu einer anderen Sportart oder Altersklasse.')
    config = m_training_defaults(sport, band)
    for kind in ('ball', 'maximal'):
        part = value.get(kind, {})
        if not isinstance(part, dict):
            raise ValueError('M-Laufform prüfen.')
        config[kind].update(deepcopy(part))
        part = config[kind]
        if type(part['enabled']) is not bool:
            raise ValueError('M-Lauf-Auswahl prüfen.')
        edge = part['edge_m']
        if type(edge) not in (int, float) or not math.isfinite(edge) or not .5 <= edge <= 100:
            raise ValueError('M-Lauf-Kantenlänge muss zwischen 0,5 und 100 m liegen.')
        if kind == 'maximal' and band in M_MAX_EDGES:
            lower, upper = M_MAX_EDGES[band]
            if not lower <= edge <= upper:
                raise ValueError(f'Maximale M-Sprints {band}: Kantenlänge {lower:g}–{upper:g} m.')
        for field in ('series', 'runs'):
            if type(part[field]) is not int or not 1 <= part[field] <= 100:
                raise ValueError('M-Lauf-Serien und Durchgänge müssen ganze Zahlen von 1 bis 100 sein.')
        seconds = part['run_seconds']
        if seconds is not None and (type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 < seconds <= 3600):
            raise ValueError('Gemessene Durchlaufzeit muss positiv sein; leer bedeutet nicht gemessen.')
        if not isinstance(part['notes'], str) or len(part['notes']) > 4000:
            raise ValueError('M-Lauf-Notizen prüfen.')
    ball = config['ball']
    if type(ball['e2_progression']) is not bool:
        raise ValueError('U11-Aufbau muss als Auswahl gespeichert sein.')
    if ball['e2_progression'] and (sport, band) != ('Fussball', 'U11'):
        raise ValueError('Der festgelegte U11-Aufbau gehört zu Fußball U11.')
    timed = ball['timed_distance_m']
    if timed is not None and (type(timed) not in (int, float) or timed not in E2_BALL_DISTANCES):
        raise ValueError('Die gemessene Ball-Durchlaufzeit einer Strecke von 70 bis 95 m zuordnen.')
    units = config['maximal']['units']
    if not isinstance(units, list) or any(type(x) is not int or not 1 <= x <= 28 for x in units) or len(units) != len(set(units)):
        raise ValueError('M-Sprint-Einheiten müssen eindeutige TE-Nummern von 1 bis 28 sein.')
    return config


def m_load_summary(part, distance_m=None):
    per_run = 4 * part['edge_m'] if distance_m is None else distance_m
    count = part['series'] * part['runs']
    seconds = part.get('run_seconds')
    if distance_m is not None and part.get('timed_distance_m') != distance_m:
        seconds = None
    return {'per_run_m': per_run, 'runs_total': count, 'total_m': per_run * count,
            'active_seconds': None if seconds is None else seconds * count}


def m_distance_text(part, distance_m=None):
    summary = m_load_summary(part, distance_m)
    geometry = (f"ca. {distance_m:g} m je Durchlauf; vier Abschnitte, rechnerisch im Mittel {distance_m / 4:g} m "
                '(Aufbau gerundet, Kurvenverlauf variabel); '
                if distance_m is not None else
                f"4 Kanten à {part['edge_m']:g} m = {summary['per_run_m']:g} m je Durchlauf; ")
    text = (geometry +
            f"{part['runs']} Durchgänge je Serie; {summary['runs_total']} Durchgänge / "
            f"{'ca. ' if distance_m is not None else ''}{summary['total_m']:g} m insgesamt")
    if summary['active_seconds'] is None:
        return text + '; Laufdauer noch nicht gemessen'
    return text + f"; Laufzeit hochgerechnet aus {part['run_seconds']:g} s je Durchlauf: {summary['active_seconds']:g} s (ohne Pausen)"


def m_training_ui(saved, sport, band, key, disabled=False):
    if saved and (saved.get('sport', sport) != sport or saved.get('band', band) != band):
        st.info('Altersklasse oder Sportart gewechselt: Die M-Laufformen zeigen jetzt die zugehörigen Startvorgaben. Erst Speichern übernimmt sie ins Profil.')
        saved = {}
    config = validate_m_training(saved or {}, sport, band)
    with st.expander('M-Läufe: Ball-Erwärmung und maximale Sprints getrennt', expanded=False):
        st.caption('Fünf Punkte ergeben vier Laufabschnitte. Kantenlänge und Gesamtstrecke pro Durchlauf werden getrennt bezeichnet. '
                   'Die Gesamtdistanz enthält keine Rückwege zwischen den Durchgängen.')
        for kind, label in (('ball', 'Mit Ball'), ('maximal', 'Ohne Ball – maximal')):
            part = config[kind]
            prefix = key + band + kind
            st.markdown('**' + label + '**')
            if kind == 'ball':
                if (sport, band) == ('Fussball', 'U11'):
                    part['e2_progression'] = st.checkbox('U11-Aufbau: Passspiel, anschließend M-Parcours ab TE 4',
                        value=part['e2_progression'], key=prefix+'progression', disabled=disabled)
                    st.caption('TE 1–3: paarweises Passspiel bis zur Mittellinie und zurück, Wende dort; links und rechts. '
                               'Ab TE 4: 70, 75, 80, 85, 90, 95 m je Durchlauf in TE 4–9; jeweils 2 × 5. '
                               'Danach bleibt 95 m als Vorlage erhalten. Sechs Stufen nach Trainingseinheiten, nicht Kalenderwochen. '
                               'Lockere Erwärmung mit Ball; enge Stangenumquerung und nachfolgende Spieler als koordinative Anforderung. '
                               'Die Strecken sind ungefähre Aufbauwerte; Abweichungen von 1–2 m ändern den Ablauf nicht.')
                else:
                    st.caption('Lockere koordinative Erwärmung: U11 24 m, U13 26 m, U15 28 m je Kante. '
                               'U11 Ausgangsumfang 2 × 5; U13/U15 vorbelegt mit 3 × 5, individuell anpassbar. '
                               'Ab U17 sowie in Leichtathletik und Skispringen keine automatische Ballform.')
            else:
                st.caption('Maximales Eins-gegen-eins ohne Ball: U11 10–15 m, U13 12–18 m, U15 15–20 m je Kante. '
                           'Ausgangsumfang 3 × 5. Die Kantenlänge wird nach tatsächlich durchgeführten Einheiten angepasst; '
                           'keine automatische Steigerung nach Kalenderwochen.')
            part['enabled'] = st.checkbox(label + ' in neue Vorlagen übernehmen',
                value=part['enabled'], key=prefix+'enabled', disabled=disabled)
            sequence = kind == 'ball' and part['e2_progression']
            cols = st.columns(3)
            low, high = M_MAX_EDGES[band] if kind == 'maximal' and band in M_MAX_EDGES else (.5, 100.)
            part['edge_m'] = cols[0].number_input(label + ': Kantenlänge (m)', low, high,
                float(part['edge_m']), .5, key=prefix+'edge', disabled=disabled or sequence)
            part['runs'] = cols[1].number_input(label + ': Durchgänge je Serie', 1, 100,
                int(part['runs']), key=prefix+'runs', disabled=disabled)
            part['series'] = cols[2].number_input(label + ': Serien', 1, 100,
                int(part['series']), key=prefix+'series', disabled=disabled)
            part['run_seconds'] = st.number_input(label + ': gemessene mittlere Durchlaufzeit (s; optional)',
                min_value=.01, max_value=3600., value=None if part['run_seconds'] is None else float(part['run_seconds']),
                step=.1, key=prefix+'seconds', disabled=disabled)
            if sequence:
                distances = [None] + list(E2_BALL_DISTANCES)
                part['timed_distance_m'] = st.selectbox('Gemessene Ballzeit gehört zu dieser Durchlaufstrecke',
                    distances, index=distances.index(part['timed_distance_m']),
                    format_func=lambda x: 'Noch nicht zugeordnet' if x is None else f'{x:g} m',
                    key=prefix+'timeddistance', disabled=disabled)
                st.caption('Die feste Kanten-Eingabe ist beim U11-Aufbau inaktiv. Die Gesamtstrecke richtet sich nach der TE. '
                           'Eine eingetragene Laufzeit wird nur bei der zugeordneten Strecke hochgerechnet.')
            else:
                st.caption(m_distance_text(part))
            if kind == 'maximal':
                part['units'] = st.multiselect('Maximale M-Sprints in diesen Trainingseinheiten',
                    list(range(1, 29)), default=part['units'], format_func=lambda x: f'TE {x}',
                    key=prefix+'units', disabled=disabled)
                st.caption('Zwei spiegelbildliche M-Parcours: Start jeweils an der Außenseite. '
                           'Der Nächste startet, wenn der Vorauslaufende die nächste Ecke erreicht. '
                           'Bei zwei Einheiten pro Woche liegt diese Sprintform in TE 2 (gerade TE-Nummern). '
                           'Ohne ausgewählte TE wird kein maximaler Sprintblock ergänzt.')
            part['notes'] = st.text_area(label + ': Technik, Pausen und Organisation', part['notes'],
                max_chars=4000, key=prefix+'notes', disabled=disabled)
        st.caption('Änderungen betreffen neue Vorlagen. Gespeicherte Sollpläne und Ist-Protokolle bleiben erhalten. '
                   'Eine gemessene mittlere Durchlaufzeit erlaubt eine Hochrechnung der Laufzeit; Pausen und Stationswechsel kommen hinzu.')
    return config


def m_training_rows(value, sport, band, te, frequency=1, short_day=False):
    config = validate_m_training(value or {}, sport, band)
    rows = []
    ball = config['ball']
    if ball['enabled']:
        technique = ('Ballführung ausschließlich links beziehungsweise rechts; bei U11 eine Serie je Fuß; enge Richtungswechsel.'
                     if sport == 'Fussball' else 'Dribbling links/rechts im Wechsel; enge Richtungswechsel.'
                     if sport == 'Basketball' else 'Ballkoordination nach eingetragener Organisationsform.')
        if ball['e2_progression'] and te < 4:
            rows.append({'Block': '01 M-Lauf mit Ball', 'Trainingsmittel': 'Paarweises Passspiel · koordinative Erwärmung',
                         'Sätze': 'Partnerwechsel im Ablauf', 'Wdh_oder_Strecke': 'Bis zur Mittellinie und zurück; dort wenden; Streckenlänge platzabhängig',
                         'Zusatzlast': 'Ball', 'Intensität': 'Locker; kontinuierliches Passspiel',
                         'Pause': 'Im gemeinsamen Erwärmungsablauf',
                         'Fokus': 'TE 1–3: im Paar fortlaufend passen, abwechselnd ausschließlich links bzw. rechts. ' + ball['notes']})
        else:
            distance_m = E2_BALL_DISTANCES[min(te - 4, len(E2_BALL_DISTANCES) - 1)] if ball['e2_progression'] else None
            if ball['e2_progression']:
                technique += ' Der Nächste folgt; enge Stangenumquerung und präzise Ballführung unter Anforderungsdruck. Aufbauwerte gerundet. '
            rows.append({'Block': '01 M-Lauf mit Ball', 'Trainingsmittel': 'M-Lauf mit Ball · koordinative Erwärmung',
                     'Sätze': f"{ball['series']} Serien", 'Wdh_oder_Strecke': m_distance_text(ball, distance_m),
                     'Zusatzlast': 'Ball', 'Intensität': 'Relativ locker; kontrollierte Ballführung',
                     'Pause': 'Ablauf-/Serienpausen gemäß Organisationsangabe',
                     'Fokus': technique + ' ' + ball['notes']})
    maximum = config['maximal']
    if maximum['enabled'] and te in maximum['units'] and (frequency == 1 or short_day):
        rows.append({'Block': 'M-Sprint ohne Ball', 'Trainingsmittel': 'M-Sprints ohne Ball · maximales Eins-gegen-eins',
                     'Sätze': f"{maximum['series']} Serien", 'Wdh_oder_Strecke': m_distance_text(maximum),
                     'Zusatzlast': 'ohne Ball / ohne Zusatzlast', 'Intensität': 'Maximal; enge Richtungswechsel',
                     'Pause': 'Startfolge an der nächsten Ecke; Serienpausen gemäß Organisationsangabe',
                     'Fokus': 'Zwei spiegelbildliche M-Parcours, Start an den Außenseiten. Der Nächste startet, '
                              'wenn der Vorauslaufende die nächste Ecke erreicht. ' + maximum['notes']})
    return rows


def validate_load_reference(value):
    if not isinstance(value,dict):raise ValueError('Ungültige Lastreferenz.')
    for k,low,high in [('rm_kg',0,500),('lower',35,45),('upper',35,45),('selected_bag',0,20),('velocity',0,20)]:
        x=value.get(k,{'lower':35,'upper':45}.get(k,0))
        if type(x) not in (int,float) or not math.isfinite(x) or not low<=x<=high:raise ValueError('Ungültige Lastreferenz: '+k)
    if value.get('lower',35)>value.get('upper',45):raise ValueError('Prozentbereich ist vertauscht.')
    if value.get('selected_bag',0) not in (0,)+POWERBAGS:raise ValueError('Powerbag nicht im hinterlegten Bestand.')
    for k in ['confirmed','apply_bag','m_sprints']:
        if k in value and type(value[k]) is not bool:raise ValueError('Ungültige Freigabe: '+k)
    for k in ['source','velocity_note']:
        if not isinstance(value.get(k,''),str) or len(value.get(k,''))>4000:raise ValueError('Ungültige Referenznotiz.')
    if value.get('velocity_kind',VBT_KINDS[0]) not in VBT_KINDS:raise ValueError('Geschwindigkeitsart prüfen.')
    if value.get('date'):
        try:date.fromisoformat(value['date'])
        except (ValueError,TypeError):raise ValueError('Referenzdatum prüfen.') from None
    if value.get('confirmed') and (value.get('rm_kg',0)<=0 or not value.get('source','').strip() or not value.get('date')):
        raise ValueError('Bestätigte Referenz benötigt Last, Datum und Beschreibung.')

def reference_result(band,reference):
    validate_load_reference(reference)
    if band not in RM_BANDS:return {'eligible':False,'reason':'Prozentrechnung erst ab Trainingsklasse U17.','bags':[]}
    if not reference.get('confirmed') or reference.get('rm_kg',0)<=0:
        return {'eligible':False,'reason':'1RM-Referenz noch nicht vollständig bestätigt.','bags':[]}
    low=reference['rm_kg']*reference.get('lower',35)/100
    high=reference['rm_kg']*reference.get('upper',45)/100
    bags=[x for x in POWERBAGS if low-1e-9<=x<=high+1e-9]
    return {'eligible':True,'low':round(low,3),'high':round(high,3),'bags':bags,
            'reason':'Passende Bestandslast wählen.' if bags else 'Kein vorhandener Powerbag liegt im berechneten Bereich. Keine automatische Lastübernahme.'}

def applied_bag(band,reference):
    result=reference_result(band,reference)
    selected=reference.get('selected_bag',0)
    return selected if result['eligible'] and reference.get('apply_bag',False) and selected in result['bags'] else None


# Gemeinsame Planungsregeln von Frank Müller, Stand 20.09.2026.
# Nur Planvorlagen: keine Messsperre, keine automatische Geräteansteuerung.
PHASE_EXERCISES={'front_squat':'Front Squat','kreuzheben':'Kreuzheben','anreiss':'Anreißen'}
PHASE_BAGS=(5,8,10,12,15,17,20)

def phase_defaults():
    return {'enabled':True,'basis':6,'jumps':3,'spruenge':3,'jumps_ready':False,'spruenge_ready':False,'references':{}}

def phase_validate(config):
    if not isinstance(config,dict):raise ValueError('Phasenplanung muss ein Objekt sein.')
    for k in ['enabled','jumps_ready','spruenge_ready']:
        if type(config.get(k,phase_defaults()[k])) is not bool:raise ValueError('Ungültige Phasenfreigabe.')
    for k in ['basis','jumps','spruenge']:
        if type(config.get(k,phase_defaults()[k])) is not int or not 1<=config.get(k,phase_defaults()[k])<=14:raise ValueError('Je Phase 1–14 Einheiten eintragen.')
    if sum(config.get(k,phase_defaults()[k]) for k in ['basis','jumps','spruenge'])>28:raise ValueError('Höchstens 28 Einheiten je Makrozyklus.')
    refs=config.get('references',{})
    if not isinstance(refs,dict) or any(k not in PHASE_EXERCISES for k in refs):raise ValueError('Übungsreferenz unbekannt.')
    for kind,ref in refs.items():
        if not isinstance(ref,dict):raise ValueError('Ungültige Übungsreferenz.')
        for k,lo,hi,default in [('kg',0,500,0),('lower',0,100,25),('upper',0,100,35),('chosen',0,500,0)]:
            x=ref.get(k,default)
            if type(x) not in (int,float) or not math.isfinite(x) or not lo<=x<=hi:raise ValueError('Ungültiger Referenzwert: '+k)
        if ref.get('lower',25)>ref.get('upper',35):raise ValueError('Prozentbereich vertauscht.')
        for k in ['confirmed','apply']:
            if type(ref.get(k,False)) is not bool:raise ValueError('Referenzfreigabe prüfen.')
        if not isinstance(ref.get('source',''),str) or len(ref.get('source',''))>4000:raise ValueError('Referenzbeschreibung prüfen.')
        if ref.get('date'):
            try:date.fromisoformat(ref['date'])
            except (ValueError,TypeError):raise ValueError('Referenzdatum prüfen.') from None
        if ref.get('confirmed') and (ref.get('kg',0)<=0 or not ref.get('date') or not ref.get('source','').strip()):raise ValueError('Bestätigte Referenz benötigt Last, Datum und Übungsausführung.')
        if kind in ('front_squat','anreiss') and ref.get('chosen',0) not in (0,)+PHASE_BAGS:raise ValueError('Powerbag nicht im Bestand.')
    return deepcopy(config)

def phase_status(config,band,te):
    cfg=phase_defaults();cfg.update(config or {})
    try:phase_validate(cfg)
    except ValueError:return 'Eingaben prüfen','Grundlast'
    if not cfg['enabled'] or band in ('U11','U13'):return 'Bestehender Plan','Bestehender Plan'
    if te>cfg['basis']+cfg['jumps']+cfg['spruenge']:return 'Zyklus abgeschlossen','Zyklus abgeschlossen'
    planned='Grundlast' if te<=cfg['basis'] else 'Jumps' if te<=cfg['basis']+cfg['jumps'] else 'Sprünge'
    if planned=='Grundlast':return planned,planned
    if not cfg['jumps_ready']:return planned,'Grundlast'
    if planned=='Jumps' or band=='U15':return planned,'Jumps'
    return planned,'Sprünge' if cfg['spruenge_ready'] else 'Jumps'

def phase_load(config,kind,band,te):
    _,effective=phase_status(config,band,te)
    ref=config.get('references',{}).get(kind,{})
    if effective not in ('Jumps','Sprünge') or not ref.get('confirmed') or not ref.get('apply'):return None
    lo=ref['kg']*ref.get('lower',25)/100;hi=ref['kg']*ref.get('upper',35)/100;chosen=ref.get('chosen',0)
    if chosen<=0 or not lo-1e-9<=chosen<=hi+1e-9:return None
    if kind in ('front_squat','anreiss') and chosen not in PHASE_BAGS:return None
    return f"{chosen:g} kg (gewählt aus {ref.get('lower',25):g}–{ref.get('upper',35):g} % der technisch sauberen {PHASE_EXERCISES[kind]}-Referenz {ref['kg']:g} kg)"

def phase_exercise_label(kind,effective):
    if effective=='Grundlast':return {'front_squat':'Front Squat – Grundlast und Technik','kreuzheben':'Kreuzheben – Grundlast und Technik','anreiss':'Anreiß-Streckung – Grundlast und Technik'}[kind]
    return PHASE_EXERCISES[kind]+(' Jumps' if effective=='Jumps' else ' Sprünge')

def phase_ui(saved,band,key,disabled=False):
    cfg=phase_defaults();cfg.update(deepcopy(saved or {}))
    with st.expander('Makrozyklus: Grundlast → Jumps → Sprünge',expanded=False):
        st.caption('Beispiel 6 + 3 + 3 Trainingseinheiten. Bei 2 TE/Woche entsprechen die letzten 6 Einheiten 3 Wochen; bei 1 TE/Woche 6 Wochen. Die Anzahl bleibt veränderbar.')
        cfg['enabled']=st.checkbox('Phasensteuerung für neue Planvorlagen verwenden',value=cfg['enabled'],key=key+'enable',disabled=disabled)
        cols=st.columns(3)
        for col,field,label in zip(cols,['basis','jumps','spruenge'],['Grundlast: Einheiten','Jumps: Einheiten','Abschlussphase: Einheiten']):
            cfg[field]=col.number_input(label,1,14,int(cfg[field]),key=key+field,disabled=disabled)
        cfg['jumps_ready']=st.checkbox('Übergang von Grundlast zu Jumps freigegeben',value=cfg['jumps_ready'],key=key+'jready',disabled=disabled)
        cfg['spruenge_ready']=st.checkbox('Ab U17: Übergang von Jumps zu Sprüngen freigegeben',value=cfg['spruenge_ready'],key=key+'sready',disabled=disabled or band not in ('U17','U20','U23','MASTER'))
        st.caption('U15: Front-Squat-Jumps; männlich Kreuzhebe-Jumps, weiblich Anreiß-Jumps. U15 bleibt auch in der Abschlussphase bei Jumps. Ab U17 können die freigegebenen Kraftübungen zu Sprüngen wechseln. Lauf-ABC und sportartspezifische Technikübungen sind davon getrennt.')
        st.caption('Die Freigaben ändern neue Vorlagen. Bereits gespeicherte Sollpläne, Ist-Werte und Messungen werden nicht rückwirkend geändert.')
        refs=deepcopy(cfg.get('references',{}))
        for kind,label in PHASE_EXERCISES.items():
            ref=deepcopy(refs.get(kind,{}))
            with st.expander(label+': technisch sauber bewältigte Referenzlast'):
                st.caption('Kein Maximalversuch erforderlich. Externe Gesamtlast und genaue Übungsausführung dokumentieren. Jede Übung hat eine eigene Bezugsgröße; keine automatische Umrechnung aus Kniebeuge auf Kreuzheben.')
                rkey=key+kind
                ref['kg']=st.number_input(label+': Referenzlast (kg; 0 = fehlt)',0.,500.,float(ref.get('kg',0)),.5,key=rkey+'kg',disabled=disabled)
                ref['source']=st.text_area(label+': Ausführung und Ermittlung',ref.get('source',''),max_chars=4000,key=rkey+'source',disabled=disabled)
                ref['date']=st.date_input(label+': Referenzdatum',date.fromisoformat(ref['date']) if ref.get('date') else date.today(),key=rkey+'date',disabled=disabled).isoformat()
                ref['confirmed']=st.checkbox(label+': Referenz bestätigt',value=ref.get('confirmed',False),key=rkey+'confirmed',disabled=disabled)
                c1,c2=st.columns(2)
                ref['lower']=c1.number_input(label+': Untergrenze (%)',0.,100.,float(ref.get('lower',25)),1.,key=rkey+'lower',disabled=disabled)
                ref['upper']=c2.number_input(label+': Obergrenze (%)',0.,100.,float(ref.get('upper',35)),1.,key=rkey+'upper',disabled=disabled)
                st.caption('25–35 % ist ein veränderbarer Ausgangsvorschlag. Geschätzte 50–70 % für Anreißen sind keine automatisch eingetragene Messung.')
                lo=ref['kg']*ref['lower']/100;hi=ref['kg']*ref['upper']/100
                st.write(f'Rechnerischer Bereich: {lo:g}–{hi:g} kg')
                if kind in ('front_squat','anreiss'):
                    options=[0]+[x for x in PHASE_BAGS if lo-1e-9<=x<=hi+1e-9]
                    old=ref.get('chosen',0)
                    ref['chosen']=st.selectbox(label+': Powerbag auswählen',options,index=options.index(old) if old in options else 0,format_func=lambda x:'Keine Übernahme' if x==0 else f'{x:g} kg',key=rkey+'chosen_'+str(options),disabled=disabled)
                    if len(options)==1:st.caption('Kein vorhandener Powerbag im Bereich; keine automatische Übernahme.')
                else:ref['chosen']=st.number_input(label+': gewählte Gesamtlast (kg)',0.,500.,float(ref.get('chosen',0)),.5,key=rkey+'chosen',disabled=disabled)
                ref['apply']=st.checkbox(label+': Last in Jumps-/Sprungphase übernehmen',value=ref.get('apply',False),key=rkey+'apply',disabled=disabled or band in ('U11','U13'))
                if ref['apply'] and (not ref['confirmed'] or not lo<=ref['chosen']<=hi or ref['chosen']<=0):st.caption('Übernahme ist noch nicht wirksam: bestätigte Referenz und passende Last erforderlich.')
                refs[kind]=ref
        cfg['references']=refs
        try:phase_validate(cfg)
        except ValueError as exc:st.warning(str(exc))
    return cfg


def validate_kader(kader):
    if not isinstance(kader, dict) or set(kader) != {"Fussball", "Leichtathletik"}:
        raise ValueError("Die Sicherung muss Fußball und Leichtathletik enthalten.")
    for sport, athletes in kader.items():
        if not isinstance(athletes, dict) or len(athletes) > 10000:
            raise ValueError("Ungültige Athletenliste.")
        for name, p in athletes.items():
            if not isinstance(name, str) or not name.strip() or len(name) > 120 or name != name.strip():
                raise ValueError("Ungültiger Athletenname.")
            if not isinstance(p, dict):
                raise ValueError("Ungültiges Athletenprofil.")
            for field, low, high in [("alter",10,40),("groesse",1.30,2.15),("gewicht",30,140),("t_60",6,15)]:
                value = p.get(field)
                if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                    raise ValueError(f"Ungültiger Wert im Feld {field}.")
            if int(p["alter"]) != p["alter"]:
                raise ValueError("Das Alter muss in ganzen Jahren angegeben sein.")
            if p.get("profil") not in VALID_PROFILES or not p["profil"].startswith(sport + "_"):
                raise ValueError("Trainingsprofil und Sportart passen nicht zusammen.")
            if p.get("fasertyp") not in ["Ausdauer", "Kraft", "Sprungkraft", "Gazelle", "Schnelligkeit (Sprint)"]:
                raise ValueError("Unbekannter Fasertyp.")
            if p.get("reife") not in ["Spätentwickler (Retardiert)", "Normalentwickler", "Frühentwickler (Akzeleriert)"]:
                raise ValueError("Unbekannter Entwicklungsstatus.")
            if not isinstance(p.get("sbe"), str) or len(p["sbe"]) > 120:
                raise ValueError("Ungültige SBE-Angabe.")
            if "geschlecht" in p and p["geschlecht"] not in ["Männlich", "Weiblich"]:
                raise ValueError("Ungültige Geschlechtsangabe.")
            if not isinstance(p.get("notizen", ""), str) or len(p.get("notizen", "")) > 4000:
                raise ValueError("Profilnotizen dürfen höchstens 4000 Zeichen enthalten.")
            if "t_150" in p:
                v = p["t_150"]
                if type(v) not in (int,float) or not math.isfinite(v) or not 0 < v <= 120:
                    raise ValueError("Ungültige 150-m-Zeit.")
            if "t_150_quelle" in p and p["t_150_quelle"] not in ["gemessen", "berechnet", "ungeklärt"]:
                raise ValueError("Ungültige Herkunft der 150-m-Zeit.")
            references = p.get("tempo_referenzen", {})
            if not isinstance(references, dict) or any(k not in {str(d) for d in [100,200,1500] + list(range(250,801,50))} for k in references):
                raise ValueError("Ungültige Streckenreferenzen für die Tempotabelle.")
            for seconds in references.values():
                if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 0 <= seconds <= 1800:
                    raise ValueError("Testzeiten müssen zwischen 0 und 1800 Sekunden liegen; 0 bedeutet fehlend.")
            validate_m_training(p.get("m_training", {}), sport, p["profil"].split("_")[1])
            validate_load_reference(p.get("lastreferenz", {}))
            phase_validate(p.get("phasensteuerung", {}))
            validate_jump_tests(p.get("sprungtests", []))
            validate_sessions(p.get("einheitenprotokoll", {}))
            rate = p.get("folge_rate", 0)
            if type(rate) not in (int, float) or not math.isfinite(rate) or not 0 <= rate <= 20:
                raise ValueError("Ungültige Folgeempfehlungsrate.")
            cycles = p.get("makrozyklen", {})
            if not isinstance(cycles, dict) or len(cycles) > 200:
                raise ValueError("Ungültige Makrozyklen.")
            active = p.get("aktiver_makrozyklus", "Bestand")
            if not isinstance(active, str) or not active.strip() or len(active) > 120:
                raise ValueError("Ungültiger Makrozyklusname.")
            for cycle_name, snapshot in cycles.items():
                if not isinstance(cycle_name, str) or not cycle_name.strip() or len(cycle_name) > 120:
                    raise ValueError("Ungültiger Archivname.")
                if not isinstance(snapshot, dict) or "makrozyklen" in snapshot or "aktiver_makrozyklus" in snapshot:
                    raise ValueError("Ungültiger Zyklusstand.")
                validate_kader({"Fussball": {name: snapshot} if sport == "Fussball" else {},
                                "Leichtathletik": {name: snapshot} if sport == "Leichtathletik" else {}})
            plan = p.get("planung", {})
            if not isinstance(plan, dict):
                raise ValueError("Ungültige Planung.")
            validate_organization(plan.get("organisation", {}))
            ranges = {"einheiten":(1,2), "startwoche":(1,52), "bag_start":(1,20),
                      "burpee_start":(1,30), "cheer_start":(0,30), "single_start":(0,30), "beid_start":(0,30),
                      "kreuzheben_last":(0,500), "bag_last":(0,30), "test_distanz":(50,1500), "test_zeit":(0,900),
                      "test_prozent":(50,100), "steigerung_wdh":(0,5), "abc_step":(0,10)}
            for key, (low, high) in ranges.items():
                value = plan.get(key)
                if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high):
                    raise ValueError(f"Ungültige Planung: {key}.")
                if value is not None and key not in ("bag_last", "test_zeit", "kreuzheben_last", "abc_step") and int(value) != value:
                    raise ValueError(f"Ganze Zahl erforderlich: {key}.")
            for key in ("progression", "kapazitaet20", "burpees_bestaetigt", "tempo_interpolation", "tempo_extrapolation"):
                if key in plan and type(plan[key]) is not bool:
                    raise ValueError(f"Ungültige Freigabe: {key}.")
            if "rolle" in plan and plan["rolle"] not in ["Automatisch nach Wochenrhythmus", "Haupttag", "Neuromuskulär / vor dem Spiel"]:
                raise ValueError("Unbekanntes Einheitsziel.")
    return deepcopy(kader)

class StorageError(Exception):
    pass

@contextmanager
def remote_connection():
    try:
        import psycopg
    except ImportError as exc:
        raise StorageError("Für die externe Datenbank fehlt psycopg. requirements.txt aktualisieren.") from exc
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=10) as con:
            yield con
    except psycopg.Error as exc:
        raise StorageError("Externe Datenbank nicht erreichbar oder nicht eingerichtet. Es wurde nicht lokal ersatzgespeichert.") from exc

def remote_load():
    with remote_connection() as con:
        con.execute("CREATE TABLE IF NOT EXISTS doc_athletic_state (id INTEGER PRIMARY KEY CHECK(id=1), revision BIGINT NOT NULL, payload TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS doc_athletic_history (revision BIGINT PRIMARY KEY, payload TEXT NOT NULL, saved_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)")
        initial = json.dumps(validate_kader(DEFAULT_KADER), ensure_ascii=False)
        con.execute("INSERT INTO doc_athletic_state VALUES (1,0,%s) ON CONFLICT (id) DO NOTHING", (initial,))
        row = con.execute("SELECT payload,revision FROM doc_athletic_state WHERE id=1").fetchone()
        return validate_kader(json.loads(row[0])), row[1]

def remote_save(kader, expected_revision):
    payload = json.dumps(validate_kader(kader), ensure_ascii=False, allow_nan=False)
    with remote_connection() as con:
        old = con.execute("SELECT revision,payload FROM doc_athletic_state WHERE id=1 FOR UPDATE").fetchone()
        if old is None or old[0] != expected_revision:
            raise StorageConflict("Eine andere Sitzung hat inzwischen gespeichert. Bitte den gespeicherten Stand neu laden.")
        con.execute("INSERT INTO doc_athletic_history(revision,payload) VALUES (%s,%s) ON CONFLICT (revision) DO NOTHING", old)
        con.execute("UPDATE doc_athletic_state SET payload=%s,revision=revision+1 WHERE id=1", (payload,))
    return expected_revision + 1

def lade_kader_von_datei():
    if DATABASE_URL:
        return remote_load()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_FILE, timeout=10)) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, payload TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS history (revision INTEGER PRIMARY KEY, payload TEXT NOT NULL, saved_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT payload, revision FROM state WHERE id=1").fetchone()
        if row is None:
            if KADER_DATEI.exists():
                with KADER_DATEI.open(encoding="utf-8") as f:
                    initial = validate_kader(json.load(f))
            else:
                initial = validate_kader(DEFAULT_KADER)
            payload = json.dumps(initial, ensure_ascii=False, allow_nan=False)
            con.execute("INSERT INTO state VALUES (1, 0, ?)", (payload,))
            row = (payload, 0)
        return validate_kader(json.loads(row[0])), row[1]

def speichere_kader_in_datei(kader, expected_revision):
    validated = validate_kader(kader)
    if DATABASE_URL:
        return remote_save(validated, expected_revision)
    payload = json.dumps(validated, ensure_ascii=False, allow_nan=False)
    with closing(sqlite3.connect(DB_FILE, timeout=10)) as con, con:
        con.execute("BEGIN IMMEDIATE")
        old = con.execute("SELECT revision, payload FROM state WHERE id=1").fetchone()
        if old is None or old[0] != expected_revision:
            raise StorageConflict("Eine andere Sitzung hat inzwischen gespeichert. Bitte den gespeicherten Stand neu laden und Änderungen erneut prüfen.")
        con.execute("INSERT OR IGNORE INTO history(revision,payload) VALUES (?,?)", old)
        con.execute("UPDATE state SET payload=?, revision=revision+1 WHERE id=1", (payload,))
    return expected_revision + 1

def warmup_text(band, te):
    if band == "U13":
        return "800 m ca. 3:40 min; Einstieg nach Trainerprüfung" if te >= 3 else "Einlaufen nach Trainerentscheidung; 800 m erst etwa ab TE 3"
    return {"U15":"800 m ca. 3:30 min", "U17":"800 m unter 3:15 min",
            "U20":"800 m unter 3:05 min", "U23":"800 m unter 2:55 min"}.get(band,
            "Einlaufen nach Trainerentscheidung; noch keine feste Zeit hinterlegt")

def weekly_reps(start, week, cap, approved, step=1):
    return min(start + ((week - 1) * step if approved else 0), cap)

def unit_context(te, units_per_week, start_week, role):
    week = start_week + (te - 1) // units_per_week
    day = (te - 1) % units_per_week + 1
    short = units_per_week == 2 and (role == "Neuromuskulär / vor dem Spiel" or (role == "Automatisch nach Wochenrhythmus" and day == 2))
    return week, day, short

def kreuzheben_load(band, last):
    if band in ["U11", "U13"]:
        return "Keine Kreuzhebe-Zusatzlast freigegeben (bisherige U11/U13-Regel)"
    if last > 0:
        return f"Gesamtlast {last:g} kg (individuelle Trainerfestlegung)"
    return "Kreuzhebe-Last und Gerät individuell festlegen"

def cheer_load(band, gender):
    if gender != "Weiblich":
        return {"U11":"1 kg je Hand","U13":"2 kg je Hand","U15":"4 kg je Hand","U17":"6 kg je Hand","U20":"8 kg je Hand","U23":"8 kg je Hand","MASTER":"8 kg je Hand"}[band]
    return {"U11":"1 kg je Hand", "U13":"2 kg je Hand", "U15":"3 kg je Hand",
            "U17":"4 kg je Hand", "U20":"4–6 kg je Hand"}.get(band, "Zusatzlast im Sollplan anhand der dokumentierten Einheit eintragen")

def exercise_row(exercise, sets, reps, load, note):
    cells = ["Ergänzung", exercise, str(sets), reps, load, note, "Stationswechsel bis 60 s"]
    return '<tr style="background:#e8f4f0">' + ''.join('<td style="padding:6px;border:1px solid #aaa">'+escape(v)+'</td>' for v in cells) + '</tr>'

class MatrixRowsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.body = False
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody': self.body = True
        elif self.body and tag == 'tr': self.row = []
        elif self.body and tag == 'td': self.cell = []

    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == 'td' and self.cell is not None:
            self.row.append(''.join(self.cell)); self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None
        elif tag == 'tbody': self.body = False

def organize_multisport_html(html, frequency, short_day, main_sets, sport, band, config, timing):
    parser = MatrixRowsParser(); parser.feed(html)
    if not parser.rows: return html
    warm, stations, running, cool = [], [], [], []
    has_ball_warmup = any(row[0] == '01 M-Lauf mit Ball' for row in parser.rows)
    for row in parser.rows:
        if has_ball_warmup and sport == 'Fussball' and band in ('U11', 'U13') and row[0] == 'Erwärmung':
            continue  # The specific ball prescription replaces the generic ball warm-up.
        if len(row) != 7: raise ValueError('Trainingsmatrix benötigt sieben Spalten.')
        row = list(row)
        if row[0] == '01 M-Lauf mit Ball':
            index = next((i for i, r in enumerate(warm) if r[0].startswith('Block 1: ABC')), len(warm))
            warm.insert(index, row)
        elif row[0] == 'Erwärmung' or row[0].startswith('Block 1: ABC'):
            if sport == 'Fussball' and band in ('U11', 'U13') and row[0] == 'Erwärmung':
                row[1] = 'Spielerische Erwärmung: Ballbeschleunigungen bis zur Mittellinie und zurück'
                row[3] = 'Wettspielform; Ballführung links/rechts im Wechsel'
                row[5] = 'Bewegungsqualität und Ballkontrolle'
            warm.append(row)
        elif row[0] == 'Cool-Down': cool.append(row)
        elif 'Lauf / Transfer' in row[0] or 'GLA Vorab' in row[0]:
            running.append(row)
        elif row[0] == 'M-Sprint ohne Ball':
            if frequency == 1 or short_day:
                running.append(row)

        else:
            if row[1].startswith('Komplextransfer: Hürdensprünge'):
                continue  # Hurdle station and short running transfer are already explicit rows.
            if frequency == 2 and not short_day and row[0] == 'Komplex: Hürden':
                continue  # Dedicated hurdle station belongs to the second session.
            row[6] = 'Stationswechsel bis 60 s; Serienpause separat'
            if frequency == 2 and not short_day: row[2] = main_sets
            stations.append(row)
    # Divide the ordered exercises into blocks of 3–5 where possible. Do not multiply
    # the running prescription when more than one block is present.
    import re
    count = max(1, math.ceil(len(stations)/5))
    groups = []
    offset = 0
    for block in range(count):
        size = len(stations)//count + (block < len(stations)%count)
        group = stations[offset:offset+size]; offset += size
        for i, row in enumerate(group, 1): row[0] = f'Block {block+1} · Station {i}'
        groups.append(group)
    transfers = [[] for _ in groups]
    for row in running:
        prescription = row[1]
        match = re.fullmatch(r'(\d+)\s*[x×]\s*(\d+\s*m.*)', prescription)
        parts = prescription.split(' + ')
        if match and int(match[1]) >= count:
            reps = int(match[1])
            for i in range(count):
                part = list(row); part[1] = f'{reps//count + (i < reps%count)} × {match[2]}'
                transfers[i].append(part)
        elif len(parts) >= count and not any(word in prescription for word in ('Abschlusstest', 'Test auf Zeit', 'vorab')):
            for i in range(count):
                a, b = i*len(parts)//count, (i+1)*len(parts)//count
                part = list(row); part[1] = ' + '.join(parts[a:b]); transfers[i].append(part)
        else:
            transfers[-1].append(row)
    rows = list(warm)
    for i, (group, transfer) in enumerate(zip(groups, transfers), 1):
        rows.extend(group)
        for row in transfer:
            row[0] = f'Nach Block {i}: Lauf / Transfer'
        rows.extend(transfer)
    rows.extend(cool)
    def render(row):
        color = '#fff2cc' if row in warm else '#f2f2f2' if row in cool else '#ddebf7' if row[0].startswith('Nach Block') else '#fce4d6'
        return '<tr style="background:'+color+';color:#111">'+''.join('<td style="padding:6px;border:1px solid #aaa">'+escape(str(cell))+'</td>' for cell in row)+'</tr>'
    body = ''.join(render(row) for row in rows)
    start, end = html.index('<tbody>')+len('<tbody>'), html.index('</tbody>')
    html = html[:start]+body+html[end:]
    note = '<p>'+escape(organization_text(frequency, config))+'</p>'
    if sport in ('Fussball', 'Leichtathletik'):
        note += '<p>Team-Style beim vorgesehenen Lauftransfer: 3–5 Personen, etwa 2 m Abstand; Führung nach aktueller Leistungsfähigkeit, Wechsel nach Abstimmung.</p>'
    note += timing_html(timing)
    return html.replace('<table ', note+'<table ', 1)


def profile_age(profile):
    band = profile.split("_")[1]
    return {"U11":10,"U13":12,"U15":14,"U17":16,"U20":19,"U23":22,"MASTER":24}[band]

def age_matches_profile(age, profile):
    # Ganze Lebensjahre; Trainer dürfen bewusst ein anderes Trainingsprofil wählen.
    band = profile.split("_")[1]
    ranges = {"U11": (9, 10), "U13": (11, 12), "U15": (13, 14),
              "U17": (15, 16), "U20": (17, 19), "U23": (20, 22), "MASTER": (23, 40)}
    low, high = ranges[band]
    return low <= age <= high

def widget_key(field, sport, mode, target):
    context = json.dumps([sport,mode,target,st.session_state.get("edit_epoch",0)], ensure_ascii=False)
    return field + "_" + hashlib.sha256(context.encode()).hexdigest()[:16]

def reload_saved():
    data, revision = lade_kader_von_datei()
    st.session_state.kader_db = data
    st.session_state.kader_revision = revision
    st.session_state.edit_epoch = st.session_state.get("edit_epoch",0) + 1


auth_fingerprint = hashlib.sha256(json.dumps([TRAINER_CODE,GAST_CODE,DATABASE_URL]).encode()).hexdigest()
if st.session_state.get("auth_fingerprint") != auth_fingerprint:
    st.session_state.clear()
    st.session_state.auth_fingerprint = auth_fingerprint

if not TRAINER_CODE:
    st.title("Doc Athletic Train Smart Evolution Software 105")
    st.info("Trainerzugang einrichten: In den Streamlit-Einstellungen unter Secrets den Eintrag DOC_ATHLETIC_TRAINER_CODE mit einem eigenen Zugangscode speichern. Danach die App neu laden.")
    st.stop()
if DATABASE_URL:
    st.caption("Speicher: externe PostgreSQL-Datenbank")
else:
    st.warning("Speicher: lokale App-Datei. Auf Streamlit Cloud nicht dauerhaft garantiert. Nach der Arbeit unter Kader-Datensicherung ein Backup herunterladen; externe Datenbank noch einrichten.")

if 'auth_modus' not in st.session_state:
    st.session_state.auth_modus = None

if st.session_state.auth_modus is None:
    col_11, col_12, col_13 = st.columns([1, 2, 1])
    with col_12:
        lade_bild(["logo.png", "logo.png.png", "logo"], use_col=True)
        st.markdown("<p style='text-align: center; color: #c5c6c7; margin-top: 20px;'>Bitte Zugriffscode eingeben (Fußball & Leichtathletik)</p>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        with col_p2:
            eingabe_code = st.text_input("Zugriffscode", type="password")
            if st.button("ZUGRIFF BESTÄTIGEN"):
                if TRAINER_CODE and hmac.compare_digest(eingabe_code.encode(), TRAINER_CODE.encode()):
                    st.session_state.auth_modus = "trainer"
                    st.rerun()
                elif GAST_CODE and hmac.compare_digest(eingabe_code.encode(), GAST_CODE.encode()):
                    st.session_state.auth_modus = "gast"
                    st.rerun()
                else:
                    st.error("Ungültiger Code. Bitte prüfen.")
                st.stop()
    st.stop()

if 'navigations_status' not in st.session_state:
    st.session_state.navigations_status = 'Start'

if 'kader_db' not in st.session_state:
    try:
        reload_saved()
    except (OSError, sqlite3.Error, StorageError, ValueError) as exc:
        st.error(f"Athletendaten konnten nicht geladen werden: {exc}. Vorhandene Dateien bleiben erhalten.")
        st.stop()

if "save_notice" in st.session_state:
    st.success(st.session_state.pop("save_notice"))

def navigiere(ziel):
    st.session_state.navigations_status = ziel

if st.session_state.get('auth_modus') == 'trainer':
    with st.sidebar.expander('Private Originalpläne (optional)'):
        st.caption('Originaldokumente bleiben getrennt vom Programmcode. Eine geladene Quelle wird nur in dieser Sitzung angeboten; gespeicherte Sollpläne bleiben im Kader-Backup erhalten.')
        source_upload = st.file_uploader('Private Quellen-Datei', type=['json'], key='private_sources_upload')
        if st.button('Private Quellen laden', disabled=source_upload is None):
            try:
                if source_upload.size > 10_000_000:
                    raise ValueError('Quellen-Datei ist zu groß.')
                payload = json.loads(source_upload.getvalue())
                sources = payload.get('sources') if isinstance(payload, dict) else None
                if not isinstance(sources, dict) or len(sources) > 1000 or any(not isinstance(k, str) or not k.strip() or len(k)>300 or not isinstance(v, str) or len(v)>100000 for k,v in sources.items()):
                    raise ValueError('Ungültige Quellen-Datei.')
                st.session_state.private_sources = sources
                st.success(f'{len(sources)} private Originalpläne geladen.')
            except (ValueError, UnicodeError) as exc:
                st.error(str(exc))
    st.sidebar.markdown('**Kader-Datensicherung**')
    st.sidebar.caption("Sicherung enthält die zuletzt gespeicherten Profile einschließlich Planungseinstellungen.")
    try:
        backup_data, _ = lade_kader_von_datei()
        st.sidebar.download_button('Kader sichern (Backup-Datei)',
            data=json.dumps(backup_data, ensure_ascii=False, indent=2),
            file_name='kader_db.json', mime='application/json')
    except (OSError, sqlite3.Error, StorageError, ValueError):
        st.sidebar.error("Die aktuelle Sicherung ist nicht verfügbar.")
    st.sidebar.caption("Neu laden verwirft noch nicht gespeicherte Eingaben.")
    if st.sidebar.button('Gespeicherten Stand neu laden'):
        try:
            reload_saved()
            st.rerun()
        except (OSError, sqlite3.Error, StorageError, ValueError) as exc:
            st.sidebar.error(str(exc))
    _upload = st.sidebar.file_uploader('Kader aus Backup laden', type=['json'])
    restore_confirm = st.sidebar.checkbox('Vorhandenen Kader durch die Sicherung ersetzen')
    if _upload is not None and st.sidebar.button('Backup jetzt wiederherstellen', disabled=not restore_confirm):
        try:
            if _upload.size > 5_000_000:
                raise ValueError("Die Sicherung ist zu groß.")
            restored = validate_kader(json.loads(_upload.getvalue()))
            rev = speichere_kader_in_datei(restored, st.session_state.kader_revision)
            st.session_state.kader_db = restored
            st.session_state.kader_revision = rev
            st.session_state.edit_epoch = st.session_state.get("edit_epoch",0) + 1
            st.session_state.save_notice = 'Kader wiederhergestellt und gespeichert.'
            st.rerun()
        except (OSError, sqlite3.Error, StorageError, ValueError, StorageConflict) as exc:
            st.sidebar.error(f"Wiederherstellung abgebrochen: {exc}")

abc_parameter = {
    "Fussball_U11": {"sets": 3, "start_m": 12.0, "step_m": 2.0, "sbe_ziel": "SR 3"},
    "Fussball_U13": {"sets": 4, "start_m": 15.0, "step_m": 2.5, "sbe_ziel": "SR 2-3"},
    "Fussball_U15_m": {"sets": 4, "start_m": 18.0, "step_m": 2.5, "sbe_ziel": "SR 2"},
    "Fussball_U15_w": {"sets": 4, "start_m": 15.0, "step_m": 2.5, "sbe_ziel": "SR 2"},
    "Fussball_U17_m": {"sets": 5, "start_m": 22.0, "step_m": 3.0, "sbe_ziel": "SR 1-2"},
    "Fussball_U17_w": {"sets": 5, "start_m": 20.0, "step_m": 2.5, "sbe_ziel": "SR 1-2"},
    "Fussball_U20_m": {"sets": 5, "start_m": 25.0, "step_m": 3.0, "sbe_ziel": "SR 1"},
    "Fussball_U20_w": {"sets": 5, "start_m": 22.0, "step_m": 2.5, "sbe_ziel": "SR 1"},
    "Fussball_U23_m": {"sets": 6, "start_m": 28.0, "step_m": 3.0, "sbe_ziel": "SR 1-0"},
    "Fussball_U23_w": {"sets": 6, "start_m": 25.0, "step_m": 2.5, "sbe_ziel": "SR 1-0"},
    "Fussball_MASTER_m": {"sets": 6, "start_m": 30.0, "step_m": 3.0, "sbe_ziel": "SR 0"},
    "Fussball_MASTER_w": {"sets": 6, "start_m": 28.0, "step_m": 3.0, "sbe_ziel": "SR 0"},
    "Leichtathletik_U11": {"sets": 3, "start_m": 12.0, "step_m": 2.0, "sbe_ziel": "SR 3"},
    "Leichtathletik_U13": {"sets": 4, "start_m": 15.0, "step_m": 2.0, "sbe_ziel": "SR 2-3"},
    "Leichtathletik_U15": {"sets": 4, "start_m": 18.0, "step_m": 2.5, "sbe_ziel": "SR 2"},
    "Leichtathletik_U17_m": {"sets": 5, "start_m": 25.0, "step_m": 3.5, "sbe_ziel": "SR 1-2"},
    "Leichtathletik_U17_w": {"sets": 5, "start_m": 22.0, "step_m": 3.0, "sbe_ziel": "SR 1-2"},
    "Leichtathletik_U20_m": {"sets": 6, "start_m": 28.0, "step_m": 3.0, "sbe_ziel": "SR 1"},
    "Leichtathletik_U20_w": {"sets": 6, "start_m": 26.0, "step_m": 3.0, "sbe_ziel": "SR 1"},
    "Leichtathletik_U23_m": {"sets": 6, "start_m": 30.0, "step_m": 3.0, "sbe_ziel": "SR 0"},
    "Leichtathletik_U23_w": {"sets": 6, "start_m": 28.0, "step_m": 3.0, "sbe_ziel": "SR 0"},
    "Leichtathletik_MASTER_m": {"sets": 6, "start_m": 30.0, "step_m": 3.0, "sbe_ziel": "SR 0"},
    "Leichtathletik_MASTER_w": {"sets": 6, "start_m": 28.0, "step_m": 3.0, "sbe_ziel": "SR 0"}
}

HARDWARE_GRIFFBAELLE = [3, 5, 7, 9]
HARDWARE_HEXBAR = [30, 35, 40, 45, 50, 55, 60, 65, 70]

def snap_to_hardware(wert, hardware_liste, konservativ=True):
    passende = [h for h in hardware_liste if (h <= wert if konservativ else h >= wert)]
    if passende:
        return max(passende) if konservativ else min(passende)
    return None

if st.sidebar.button("ABMELDEN"):
    st.session_state.clear()
    st.rerun()

if st.session_state.auth_modus == "gast":
    st.sidebar.warning("GAST-MODUS (Nur Leserechte)")

if st.session_state.navigations_status == 'Start':
    st.markdown("<h1 style='text-align: center; color: #66fcf1 !important; margin-top: 30px;'>DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE 105</h1><p style='text-align:center'>Modul 1 · Version 105 · Grundlast → Jumps → Sprünge · Tempotabellen bis 800 m</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #c5c6c7; font-size: 16px;'>Fußball & Leichtathletik · Individuelle Trainingsplanung</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lade_bild(["logo.png", "logo.png.png", "logo"], use_col=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("SYSTEM INITIALISIEREN >>", on_click=navigiere, args=('Uebersicht',))

elif st.session_state.navigations_status == 'Uebersicht':
    st.title("Systemübersicht & Athleten-Datenbank")
    st.markdown("## Komplex-Training im Nachwuchs bis Hochleistungssport (Fußball & Leichtathletik)")
    st.markdown("---")
    bild_geladen = lade_bild(["übersicht.png", "uebersicht.png", "uebersicht.png.png"], use_col=True)
    if not bild_geladen:
        st.markdown("<div style='text-align: center; border: 1px dashed #45a29e; padding: 30px;'><strong>[übersicht.png / uebersicht.png] im Verzeichnis hinterlegen.</strong></div>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button("<< ZURÜCK", on_click=navigiere, args=('Start',))
    with col2:
        st.button("OPERATIVES MENÜ STARTEN >>", on_click=navigiere, args=('Operativ',))

elif st.session_state.navigations_status == 'Operativ':
    col_top1, col_top2 = st.columns([1, 4])
    with col_top1:
        st.button("<< ÜBERSICHT", on_click=navigiere, args=('Uebersicht',))
    with col_top2:
        st.markdown("## Operative Trainingssteuerung")

    st.markdown("<div class='steuermatrix'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #66fcf1 !important; font-size: 26px; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 0; margin-bottom: 5px;'>Biometrische Live-Steuerung & Disziplin-Wahl</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0aab2; font-size: 14px; margin-bottom: 15px;'>Fokussierte Trainingsansteuerung nach Doc Athletic Train Smart Philosophie</p>", unsafe_allow_html=True)
    
    sport_kategorie = st.radio("Sportart wählen", ["⚽ Fußball", "🏃 Leichtathletik"], horizontal=True, label_visibility="collapsed")
    
    if "Fußball" in sport_kategorie:
        aktive_kategorie = "Fussball"
        aktive_sport_schluessel = [k for k in abc_parameter.keys() if "Fussball" in k]
        st.markdown("<div style='text-align: center; margin-top: 10px;'><span class='badge-fussball'>⚽ Modul: Fußball aktiv (Kernsportart)</span></div>", unsafe_allow_html=True)
    else:
        aktive_kategorie = "Leichtathletik"
        aktive_sport_schluessel = [k for k in abc_parameter.keys() if "Leichtathletik" in k]
        st.markdown("<div style='text-align: center; margin-top: 10px;'><span class='badge-leichtathletik'>🏃 Modul: Leichtathletik aktiv (Peripher)</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    aktive_athleten_db = st.session_state.kader_db[aktive_kategorie]

    athlete_actions = st.container()
    jump_area = st.container()

    pending = st.session_state.pop("pending_athlete_selection", None)
    if pending and pending[0] == aktive_kategorie and pending[1] in aktive_athleten_db:
        st.session_state[f"athlet_{aktive_kategorie}"] = pending[1]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        modus = st.selectbox("Steuerungs-Ebene", ["Einzelathlet / Einzelathletin", "Gruppe / Team (Kader)"])
        if modus == "Einzelathlet / Einzelathletin":
            if len(aktive_athleten_db) > 0:
                ziel = st.selectbox("Ziel (Name)", list(aktive_athleten_db.keys()), key=f"athlet_{aktive_kategorie}")
                aktuelle_daten = aktive_athleten_db[ziel]
                profil_soll = aktuelle_daten["profil"]
            else:
                ziel = "Neuer Athlet"
                aktuelle_daten = {"alter": 10, "groesse": 1.50, "gewicht": 35.0, "profil": aktive_sport_schluessel[0], "fasertyp": "Schnelligkeit (Sprint)", "reife": "Normalentwickler", "sbe": "SR 2", "t_60": 7.80}
                profil_soll = aktive_sport_schluessel[0]
        else:
            ziel = st.selectbox("Ziel (Kader / Profil)", aktive_sport_schluessel, key=f"kader_{aktive_kategorie}")
            profil_soll = ziel
            aktuelle_daten = {"alter": profile_age(ziel), "groesse": 1.50 if profile_age(ziel) <= 12 else 1.75, "gewicht": 35.0 if profile_age(ziel) <= 12 else 65.0, "fasertyp": "Schnelligkeit (Sprint)", "reife": "Normalentwickler", "sbe": abc_parameter[ziel]["sbe_ziel"], "t_60": 7.80}

    key_for = lambda field: widget_key(field, aktive_kategorie, modus, ziel)

    with c2:
        alter = st.number_input("Alter (Jahre)", min_value=10, max_value=40, value=int(aktuelle_daten["alter"]), key=key_for("alter"), disabled=(st.session_state.auth_modus == "gast" or modus == "Gruppe / Team (Kader)"))
        geschlecht_wahl = st.selectbox("Geschlecht", ["Männlich", "Weiblich"], index=1 if aktuelle_daten.get("geschlecht", "Weiblich" if profil_soll.endswith("_w") else "Männlich") == "Weiblich" else 0, key=key_for("geschlecht"), disabled=(st.session_state.auth_modus == "gast"))

    with c3:
        groesse = st.number_input("Körpergröße (m)", min_value=1.30, max_value=2.15, value=float(aktuelle_daten.get("groesse", 1.70)), step=0.01, key=key_for("groesse"), disabled=(st.session_state.auth_modus == "gast"))
        gewicht = st.number_input("Körpergewicht (kg)", min_value=30.0, max_value=140.0, value=float(aktuelle_daten.get("gewicht", 55.0)), step=0.5, key=key_for("gewicht"), disabled=(st.session_state.auth_modus == "gast"))

    with c4:
        ft_liste = ["Ausdauer", "Kraft", "Sprungkraft", "Gazelle", "Schnelligkeit (Sprint)"]
        reife_liste = ["Spätentwickler (Retardiert)", "Normalentwickler", "Frühentwickler (Akzeleriert)"]
        ft_idx = ft_liste.index(aktuelle_daten["fasertyp"]) if aktuelle_daten["fasertyp"] in ft_liste else 4
        ft = st.selectbox("Fasertyp", ft_liste, index=ft_idx, key=key_for("fasertyp"), disabled=(st.session_state.auth_modus == "gast"))
        reife_val = aktuelle_daten["reife"]
        r_idx = 0 if "Spät" in reife_val else 2 if "Früh" in reife_val else 1
        reife = st.selectbox("Entwicklungsstatus", reife_liste, index=r_idx, key=key_for("reife"), disabled=(st.session_state.auth_modus == "gast"))

    c_opt1, c_opt2 = st.columns(2)
    with c_opt1:
        te_wahl = st.selectbox("Trainingseinheit (TE)", [f"TE {i}" for i in range(1, 29)] + ["Alle TEs (1-14)","Alle TEs (1-28)"])
    with c_opt2:
        st.caption("Die Ausführung der belasteten Hauptübungen folgt der Phasensteuerung unten.")

    sbe_ziel = st.text_input("SBE (Reserve)", value=aktuelle_daten["sbe"], key=key_for("sbe"), disabled=(st.session_state.auth_modus == "gast"))

    if modus == "Einzelathlet / Einzelathletin":
        profil_soll = st.selectbox("Trainingsprofil / Altersklasse", aktive_sport_schluessel,
            index=aktive_sport_schluessel.index(profil_soll), key=key_for("profil"),
            disabled=(st.session_state.auth_modus == "gast"))
    else:
        st.caption("Gruppenmodus: Das Alter ist ein Referenzwert der gewählten Altersklasse; Körpermaße und Testzeiten sind Beispiele und müssen angepasst werden.")

    base_prof = profil_soll.rsplit('_', 1)[0] if ('_m' in profil_soll or '_w' in profil_soll) else profil_soll
    suffix = "_w" if geschlecht_wahl == "Weiblich" else "_m"
    if f"{base_prof}{suffix}" in abc_parameter:
        profil_soll = f"{base_prof}{suffix}"

    band = profil_soll.split("_")[1]
    profile_notes = st.text_area("Individuelle Profilnotizen", value=aktuelle_daten.get("notizen", ""),
        max_chars=4000, key=key_for("profilnotizen"), disabled=(st.session_state.auth_modus == "gast"))
    # Load prescriptions use the selected category; actual age remains separate.
    plan_age = profile_age(profil_soll)
    if modus == "Einzelathlet / Einzelathletin" and not age_matches_profile(int(alter), profil_soll):
        st.warning("Alter und gewählte Trainingsklasse weichen ab. Die Trainingsklasse steuert den Plan; bitte prüfen.")
    saved_plan = aktuelle_daten.get("planung", {})
    if modus == "Einzelathlet / Einzelathletin" and ziel in aktive_athleten_db:
        with st.expander("Makrozyklen: anlegen und wieder aufrufen"):
            active_cycle = aktuelle_daten.get("aktiver_makrozyklus", "Bestand")
            st.write(f"Aktueller Makrozyklus: {active_cycle}")
            st.caption("Zuerst Profiländerungen oben speichern. Ein neuer Zyklus archiviert den gespeicherten Stand, übernimmt die Vorgaben und beginnt bei Woche 1. Tests bleiben im Athletenverlauf erhalten.")
            cycle_name = st.text_input("Name des neuen Makrozyklus", key=key_for("cycle_name"), disabled=st.session_state.auth_modus == "gast").strip()
            create_cycle = st.button("Neuen Makrozyklus anlegen", disabled=st.session_state.auth_modus == "gast")
            archives = aktuelle_daten.get("makrozyklen", {})
            chosen_cycle = st.selectbox("Gespeicherten Makrozyklus wählen", ["Bitte wählen"] + list(archives), key=key_for("cycle_select"))
            switch_cycle = st.button("Makrozyklus aufrufen", disabled=st.session_state.auth_modus == "gast" or chosen_cycle == "Bitte wählen")
            if create_cycle or switch_cycle:
                try:
                    updated = deepcopy(st.session_state.kader_db)
                    rec = updated[aktive_kategorie][ziel]
                    saved = deepcopy(rec)
                    saved.pop("makrozyklen", None)
                    saved.pop("aktiver_makrozyklus", None)
                    saved.pop("einheitenprotokoll", None)
                    archive = deepcopy(rec.get("makrozyklen", {}))
                    if create_cycle:
                        if not cycle_name or len(cycle_name) > 120 or cycle_name == active_cycle or cycle_name in archive:
                            raise ValueError("Bitte einen neuen, eindeutigen Zyklusnamen bis 120 Zeichen eingeben.")
                        archive[active_cycle] = saved
                        rec["planung"] = deepcopy(rec.get("planung", {}))
                        rec["planung"]["startwoche"] = 1
                        rec["planung"]["progression"] = False
                        rec["phasensteuerung"]=deepcopy(rec.get("phasensteuerung",phase_defaults()))
                        rec["phasensteuerung"].update(jumps_ready=False,spruenge_ready=False)
                        rec["aktiver_makrozyklus"] = cycle_name
                    else:
                        restored = deepcopy(archive.pop(chosen_cycle))
                        archive[active_cycle] = saved
                        # Tests gehören zum Athleten, nicht zum Zyklus.
                        restored["sprungtests"] = deepcopy(rec.get("sprungtests", []))
                        restored["einheitenprotokoll"] = deepcopy(rec.get("einheitenprotokoll", {}))
                        rec = restored
                        rec["aktiver_makrozyklus"] = chosen_cycle
                    rec["makrozyklen"] = archive
                    updated[aktive_kategorie][ziel] = rec
                    revision = speichere_kader_in_datei(updated, st.session_state.kader_revision)
                    st.session_state.kader_db = updated
                    st.session_state.kader_revision = revision
                    st.session_state.edit_epoch = st.session_state.get("edit_epoch", 0) + 1
                    st.session_state.save_notice = "Makrozyklus gespeichert und geöffnet."
                    st.rerun()
                except (OSError, sqlite3.Error, StorageError, StorageConflict, ValueError) as exc:
                    st.error(f"Makrozyklus nicht geändert: {exc}")

    guest = st.session_state.auth_modus == "gast"
    with st.expander("Wochenplanung und individuelle Vorgaben", expanded=True):
        st.caption("Wochensteuerung vom 20.09.2026: Standard ist eine vollständige zusätzliche Athletikeinheit; zwei Einheiten werden ausdrücklich gewählt.")
        pc1, pc2 = st.columns(2)
        with pc1:
            einheiten = st.number_input("Einheiten pro Woche", 1, 2, int(saved_plan.get("einheiten",1)), key=key_for("einheiten"), disabled=guest)
            startwoche = st.number_input("Startwoche für TE 1", 1, 52, int(saved_plan.get("startwoche",1)), key=key_for("startwoche"), disabled=guest)
            roles = ["Automatisch nach Wochenrhythmus", "Haupttag", "Neuromuskulär / vor dem Spiel"]
            role = st.selectbox("Einheitsziel", roles, index=roles.index(saved_plan.get("rolle",roles[0])), key=key_for("rolle"), disabled=guest or einheiten == 1)
            progression = st.checkbox("Wöchentliche Steigerung nach Belastungsprüfung freigegeben", value=saved_plan.get("progression",False), key=key_for("progression"), disabled=guest)
            rep_step = st.number_input("Steigerung: Wiederholungen je Woche (je Seite bei Wechselübungen)", 0, 5, int(saved_plan.get("steigerung_wdh",1)), key=key_for("rep_step"), disabled=guest)
            abc_step = st.number_input("Lauf-ABC: Steigerung in Metern je Woche", 0.0, 10.0, float(saved_plan.get("abc_step",abc_parameter[profil_soll]["step_m"])), step=0.5, key=key_for("abc_step"), disabled=guest)
            bag_start = st.number_input("Powerbag: Startwiederholungen", 1, 20, int(saved_plan.get("bag_start",10)), key=key_for("bagstart"), disabled=guest)
            capacity = st.checkbox("Individuelles Kapazitätsziel bis 20 Wiederholungen", value=saved_plan.get("kapazitaet20",False), key=key_for("capacity"), disabled=guest)
            bag_override = st.number_input("Individuelle Powerbag-Last (kg; 0 = Korridor)", 0.0, 30.0, float(saved_plan.get("bag_last",0)), step=0.5, key=key_for("bagload"), disabled=guest)
            kreuzheben_last = st.number_input("Kreuzheben: Gesamtlast (kg; 0 = offen)", 0.0, 500.0, float(saved_plan.get("kreuzheben_last",0)), step=0.5, key=key_for("kreuzheben_last"), disabled=guest or band in ["U11","U13"])
            st.caption("Eigenständige Kraft-Hauptübung. Die Last wird nicht aus dem Sprungmodus oder Cheerleading abgeleitet. Für U11/U13 bleibt die bisherige Zusatzlast-Sperre bestehen.")
        with pc2:
            burpee_start = st.number_input("Burpees: Startwiederholungen (vorläufig 8 w / 10 m)", 1, 30, int(saved_plan.get("burpee_start",8 if geschlecht_wahl=="Weiblich" else 10)), key=key_for("burpeestart_"+geschlecht_wahl), disabled=guest)
            burpees_ok = st.checkbox("Burpee-Startwert für diesen Athleten bestätigt", value=saved_plan.get("burpees_bestaetigt",False), key=key_for("burpeeok"), disabled=guest)
            cheer_start = st.number_input("Cheerleading: Start je Arm (0 = offen)", 0, 30, int(saved_plan.get("cheer_start",0)), key=key_for("cheerstart"), disabled=guest)
            single_start = st.number_input("Einbeiniger Curl: Start je Bein (0 = offen)", 0, 30, int(saved_plan.get("single_start",0)), key=key_for("singlestart"), disabled=guest)
            bilateral_start = st.number_input("Beidbeiniger Curl: Startwiederholungen (0 = offen)", 0, 30, int(saved_plan.get("beid_start",0)), key=key_for("bilatstart"), disabled=guest)
            st.caption("Cheerleading: beidbeinige Fußgelenksprünge, Arme wechselseitig vertikal, neutraler Griff. Last gilt je Kurzhantel. Powerbar-Angaben gelten für die gesamte Stange.")
        if bag_start > 15 and not capacity:
            st.warning("Für mehr als 15 Powerbag-Wiederholungen das individuelle Kapazitätsziel aktivieren. Aktuell begrenzt der Plan auf 15.")
        st.markdown("**Tempolauf aus einem Test derselben Distanz**")
        tc1, tc2, tc3 = st.columns(3)
        test_distance = tc1.number_input("Testdistanz (m)",50,1500,int(saved_plan.get("test_distanz",800)),key=key_for("testdist"),disabled=guest)
        test_seconds = tc2.number_input("Gemessene Testzeit (Sekunden; 0 = fehlt)",0.0,900.0,float(saved_plan.get("test_zeit",0)),step=0.1,key=key_for("testtime"),disabled=guest)
        test_percent = tc3.number_input("Zieltempo (% der Testgeschwindigkeit)",50,100,int(saved_plan.get("test_prozent",80)),key=key_for("testpercent"),disabled=guest)
        st.caption("Einlaufen und Tempolauf bleiben getrennt. Keine automatische Ableitung durch Abzug von 10–15 Sekunden; keine Umrechnung dieses Tests auf andere Distanzen.")
    org_config = organization_ui(saved_plan.get("organisation", {}), einheiten, key_for("org_"), guest)
    plan_settings = {"steigerung_wdh":rep_step,"abc_step":abc_step,"einheiten":einheiten,"startwoche":startwoche,"rolle":role,"progression":progression,
        "kreuzheben_last":kreuzheben_last,"bag_start":bag_start,"kapazitaet20":capacity,"bag_last":bag_override,"burpee_start":burpee_start,
        "burpees_bestaetigt":burpees_ok,"cheer_start":cheer_start,"single_start":single_start,"beid_start":bilateral_start,
        "test_distanz":test_distance,"test_zeit":test_seconds,"test_prozent":test_percent,"organisation":org_config}

    phase_config=phase_ui(aktuelle_daten.get("phasensteuerung",{}),band,key_for("phase_"),guest)
    reference_saved=aktuelle_daten.get("lastreferenz",{})
    load_reference=deepcopy(reference_saved)
    with st.expander("Dokumentierte Geschwindigkeit / frühere Referenz"):
        st.caption("Keine Sensoranbindung, keine automatische Laständerung und keine Messsperre. Die frühere 1RM-Referenz wird nur als Altangabe erhalten; die neue Phasensteuerung nutzt eigene Übungsreferenzen.")
        st.caption(MACHINE_REFERENCE_NOTE)
        if reference_saved.get("rm_kg",0):st.write(f"Frühere Kniebeuge-Referenz: {reference_saved['rm_kg']:g} kg; nicht automatisch übernommen.")
        load_reference["velocity"]=st.number_input("Dokumentierte Hubgeschwindigkeit (m/s; 0 = fehlt)",0.,20.,float(reference_saved.get("velocity",0)),.01,key=key_for("velocity"),disabled=guest)
        load_reference["velocity_note"]=st.text_area("Geschwindigkeitsmessung: Übung, Last, Gerät und Datum",reference_saved.get("velocity_note",""),max_chars=4000,key=key_for("velocity_note"),disabled=guest)
    m_config = m_training_ui(aktuelle_daten.get("m_training", {}), aktive_kategorie, band, key_for("m_training_"), guest)

    diag_col1, diag_col2 = st.columns(2)
    with diag_col1:
        t_60 = st.number_input("60m-Referenz (s)", min_value=6.0, max_value=15.0, value=float(aktuelle_daten.get("t_60", 7.80)), step=0.01, key=key_for("t_60"), disabled=(st.session_state.auth_modus == "gast"))
    with diag_col2:
        auto_150 = round(t_60 * 2.375, 2)
        quellen = ["berechnet", "gemessen", "ungeklärt"]
        quelle_default = aktuelle_daten.get("t_150_quelle", "ungeklärt" if "t_150" in aktuelle_daten else "berechnet")
        quelle_150 = st.selectbox("Herkunft der 150-m-Zeit", quellen, index=quellen.index(quelle_default),
            key=key_for("quelle150"), disabled=(st.session_state.auth_modus == "gast"))
        if quelle_150 == "berechnet":
            t_150 = auto_150
            st.metric("150-m-Richtwert (berechnet)", f"{t_150:.2f} s")
        else:
            t_150 = st.number_input("150m-Referenz (s)", min_value=0.01, max_value=120.0,
                value=float(aktuelle_daten.get("t_150", auto_150)), step=0.01,
                key=key_for("t_150"), disabled=(st.session_state.auth_modus == "gast"))
            if quelle_150 == "ungeklärt":
                st.caption("Übernommener Wert: Bitte bestätigen, ob diese Zeit gemessen wurde.")

    with st.expander("Referenzzeiten und Tempotabelle bis 800 m", expanded=True):
        st.caption("Hier deine Referenzzeiten in Sekunden eintragen, z. B. 132 für 2:12 Minuten. Praktische Richtwerte sind möglich. 0 bedeutet: fehlt. Einlaufzeiten bleiben separat.")
        reference_columns = st.columns(3)
        saved_references = aktuelle_daten.get("tempo_referenzen", {})
        tempo_references = {}
        for index, distance in enumerate([100,200] + list(range(250,801,50)) + [1500]):
            with reference_columns[index % 3]:
                tempo_references[str(distance)] = st.number_input(
                    f"{distance} m: Referenzzeit (s; 0 = fehlt)", min_value=0.0, max_value=1800.0,
                    value=float(saved_references.get(str(distance),0)), step=0.1,
                    key=key_for(f"tempo_ref_{distance}"), disabled=guest)
        st.caption("Ein vorhandener Einzeltest aus der Wochenplanung wird für seine Strecke verwendet, solange hier keine eigene Streckenreferenz eingetragen ist. Die Zeiten werden mit dem Athletenprofil gespeichert.")
        tempo_interpolation = st.checkbox("Zwischenstrecken als individuelle Richtwerte berechnen", value=saved_plan.get("tempo_interpolation",True), key=key_for("tempo_interp"), disabled=guest)
        tempo_extrapolation = st.checkbox("Richtwerte über die längste Referenz hinaus zulassen (bis 800 m)", value=saved_plan.get("tempo_extrapolation",False), key=key_for("tempo_extra"), disabled=guest)
        st.caption("Für längere Strecken mindestens eine längere Referenz ergänzen, etwa 600 oder 800 m. Die Berechnung verbindet deine Zeiten abschnittsweise. Fortsetzungen benötigen eine Referenz ab 300 m und reichen höchstens bis zur doppelten Referenzstrecke. Es handelt sich um Planungsrichtwerte.")
    plan_settings.update({"tempo_interpolation":tempo_interpolation,"tempo_extrapolation":tempo_extrapolation})
    points = sorted((int(d),t) for d,t in tempo_references.items() if t > 0)
    if any(t2 <= t1 for (_,t1),(_,t2) in zip(points,points[1:])):
        st.warning("Bitte die Referenzzeiten prüfen: Eine längere Strecke hat eine gleich kurze oder kürzere Zeit. Für den betroffenen Bereich werden keine Richtwerte interpoliert.")

    if (test_seconds > 0 and tempo_references.get(str(test_distance),0) > 0
            and not math.isclose(tempo_references[str(test_distance)],test_seconds)):
        st.warning("Für dieselbe Strecke sind zwei Testzeiten eingetragen. Die Tempotabelle verwendet die Streckenreferenz aus ‚Testzeiten bis 800 m‘; der Einzeltest-Rechner verwendet seine eigene Eingabe. Bitte die Werte abgleichen.")

    if modus == "Einzelathlet / Einzelathletin" and st.session_state.auth_modus == "trainer":
        with athlete_actions:
            st.subheader("Athletin / Athlet anlegen und speichern")
            neuer_name = st.text_input("Neuen Athleten-Namen eingeben (zum Anlegen):", value="", key=key_for("neu")).strip()
            speichern = st.button("Athleten-Profil in Sektion speichern", type="primary")
            st.caption("Neues Profil: Namen eingeben, unten die Werte anpassen und hier speichern. Bestehendes Profil: Namensfeld leer lassen. Vor dem Athletenwechsel speichern.")
        if speichern:
            ziel_name = neuer_name if neuer_name else ziel
            try:
                if not aktive_athleten_db and not neuer_name:
                    raise ValueError("Bitte zuerst einen Athletennamen eingeben.")
                if neuer_name and neuer_name in st.session_state.kader_db[aktive_kategorie]:
                    raise ValueError("Dieser Name ist bereits vorhanden. Bitte das vorhandene Profil auswählen.")
                updated = deepcopy(st.session_state.kader_db)
                record = deepcopy(aktuelle_daten)
                if neuer_name:
                    record.pop("sprungtests", None)
                    record.pop("makrozyklen", None)
                    record.pop("aktiver_makrozyklus", None)
                    record.pop("einheitenprotokoll", None)
                record.update({"alter": int(alter), "groesse": float(groesse), "gewicht": float(gewicht), "profil": profil_soll,
                    "phasensteuerung":({**phase_config,"references":{},"jumps_ready":False,"spruenge_ready":False} if neuer_name and ziel in aktive_athleten_db else phase_config), "lastreferenz":({} if neuer_name and ziel in aktive_athleten_db else load_reference), "geschlecht": geschlecht_wahl, "fasertyp": ft, "reife": reife, "sbe": sbe_ziel, "notizen": profile_notes,
                    "m_training": (m_training_defaults(aktive_kategorie, band) if neuer_name and ziel in aktive_athleten_db else m_config),
                    "t_60": float(t_60), "t_150": float(t_150), "t_150_quelle": quelle_150, "planung":plan_settings, "tempo_referenzen":tempo_references})
                updated[aktive_kategorie][ziel_name] = record
                revision = speichere_kader_in_datei(updated, st.session_state.kader_revision)
                st.session_state.kader_db = updated
                st.session_state.kader_revision = revision
                st.session_state.pending_athlete_selection = (aktive_kategorie, ziel_name)
                st.session_state.edit_epoch = st.session_state.get("edit_epoch", 0) + 1
                st.session_state.save_notice = f"Profil {ziel_name} gespeichert und zur Bearbeitung ausgewählt."
                st.rerun()
            except (OSError, sqlite3.Error, StorageError, ValueError, StorageConflict) as exc:
                athlete_actions.error(f"Nicht gespeichert: {exc}")

    with jump_area:
        if modus == "Einzelathlet / Einzelathletin":
            with st.expander("Sprungtests: Fünfer-Hop, Schlusssprung und Seitensymmetrie", expanded=False):
                st.caption("Fünfer-Hop: fünf einbeinige Sprünge fortlaufend je Seite. Fünfer-Schlusssprung: fünf beidbeinige Sprünge ohne Haltepunkt. Gemessen wird jeweils die Gesamtweite in Metern; der beste von drei Versuchen zählt.")
                st.caption("Abweichung = |links − rechts| / Mittelwert beider Bestweiten × 100. Ab 4 % erfolgt nur ein Anzeigehinweis; die Erfassung bleibt uneingeschränkt möglich. 0 bedeutet fehlend oder ungültig und wird nicht als Leistung gewertet.")
                history = aktuelle_daten.get("sprungtests", [])
                if history:
                    summaries = [jump_summary(t) for t in history]
                    st.dataframe(pd.DataFrame(summaries), hide_index=True, width="stretch")
                    deviation = summaries[-1]["Abweichung (%)"]
                    if deviation is not None and deviation >= 4:
                        st.warning(f"Seitendifferenz im zuletzt erfassten Test: {deviation:.2f} %. Anzeigehinweis ab 4 %; keine Sperre oder Messunterbrechung.")
                    rows = []
                    for test in history:
                        row = jump_summary(test)
                        for field, label in JUMP_TESTS.items():
                            for i, value in enumerate(test[field], 1):
                                row[f"{label}: Versuch {i} (m)"] = value or None
                        rows.append(row)
                    st.download_button("Sprungtest-Verlauf herunterladen (CSV)",
                        pd.DataFrame(rows).to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                        file_name="Doc_Athletic_Sprungtests.csv", mime="text/csv")
                else:
                    st.info("Noch keine Sprungtests für dieses Profil gespeichert.")
                if ziel not in aktive_athleten_db:
                    st.info("Zuerst oben die Athletin oder den Athleten anlegen und speichern. Danach hier die Tests eintragen.")
                elif not guest:
                    st.write(f"Neuer Test für: {ziel}")
                    st.caption("Dieser Knopf speichert nur den Test. Änderungen an den übrigen Profilwerten bitte zusätzlich oben speichern. Frühere Tests bleiben erhalten.")
                    jump_epoch_key = key_for("sprung_epoch")
                    jump_epoch = st.session_state.get(jump_epoch_key, 0)
                    jump_key = lambda field: key_for(f"{field}_{jump_epoch}")
                    with st.form(jump_key("sprungtest_form")):
                        test_date = st.date_input("Datum des Sprungtests", value=date.today(), key=jump_key("sprungdatum"))
                        attempts = {}
                        for field, label in JUMP_TESTS.items():
                            st.markdown(f"**{label}**")
                            cols = st.columns(3)
                            attempts[field] = [cols[i].number_input(
                                f"{label} – Versuch {i+1} (m)", min_value=0.0, max_value=100.0,
                                value=0.0, step=0.01, format="%.2f", key=jump_key(f"sprung_{field}_{i}")) for i in range(3)]
                        notes = st.text_area("Technikbeobachtung / Bedingungen", max_chars=4000,
                            help="Abrollen über den ganzen Fuß, Fuß-Knie-Hüftstreckung, Schwungbeineinsatz, Rhythmus sowie Untergrund und Schuhe.", key=jump_key("sprungnotizen"))
                        add_test = st.form_submit_button("Sprungtest zum Verlauf speichern")
                    if add_test:
                        new_test = {"datum": test_date.isoformat(), "notizen": notes, **attempts}
                        try:
                            validate_jump_tests([new_test])
                            updated = deepcopy(st.session_state.kader_db)
                            updated[aktive_kategorie][ziel].setdefault("sprungtests", []).append(new_test)
                            revision = speichere_kader_in_datei(updated, st.session_state.kader_revision)
                            st.session_state.kader_db = updated
                            st.session_state.kader_revision = revision
                            st.session_state[jump_epoch_key] = jump_epoch + 1
                            st.session_state.save_notice = f"Sprungtest für {ziel} gespeichert."
                            st.rerun()
                        except (OSError, sqlite3.Error, StorageError, ValueError, StorageConflict) as exc:
                            st.error(f"Test nicht gespeichert: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

    reife_intern = "Spätentwickler" if "Spät" in reife else "Frühentwickler" if "Früh" in reife else "Normalentwickler"

    st.subheader("Testzeiten und berechnete Richtwerte")
    calc_100 = round(t_60 * 1.615, 2)
    calc_200 = round(t_60 * 3.265, 2)

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown("#### Eingaben und Modellwerte")
        st.write(f"60m: **{t_60:.2f} s** | 100m: **{calc_100:.2f} s** | 150m: **{t_150:.2f} s** | 200m: **{calc_200:.2f} s**")
    with res_col2:
        st.info("Die Übersicht zeigt die bisherigen Kurzsprint-Richtwerte. In der Tempotabelle haben deine eingetragenen Referenzzeiten Vorrang.")

    st.markdown("---")
    st.subheader("Tempotabellen 50–800 m")
    st.caption("100–50 % beziehen sich auf die mittlere Geschwindigkeit der jeweiligen Referenzleistung. Beispiel: 180 s bei 100 % ergeben 225 s bei 80 %. Das sind keine Anteile der maximalen momentanen Sprintgeschwindigkeit.")
    tempo_data = build_tempo_table(t_60,t_150,quelle_150,tempo_references,test_distance,test_seconds,tempo_interpolation,tempo_extrapolation)
    st.dataframe(pd.DataFrame(tempo_data), hide_index=True, width="stretch", height=670)
    if any(row["Herkunft"] == "Längere Referenz ergänzen" for row in tempo_data):
        st.info("Für die noch leeren Strecken eine längere Referenzzeit ergänzen oder die Fortsetzung der Richtwerte aktivieren. Deine eingetragenen Referenzen haben immer Vorrang.")

    st.markdown("---")
    st.subheader(f"Detaillierter Trainingsplan & Doc-Athletic-Farbkodierung: {ziel}")

    vorgaben = abc_parameter.get(profil_soll, {"sets": 4, "start_m": 15.0, "step_m": 2.5})
    te_liste = range(1,29 if "28" in te_wahl else 15) if "Alle" in te_wahl else [int(te_wahl.replace("TE ", ""))]

    # ========================================================================
    # POWER BAGS: REALISTISCHE VON-BIS-KORRIDORE (BIS 17 KG) & 12-15 WDH.
    # ========================================================================
    if plan_age <= 13:
        bag_text = "Power Bag 5-8 kg"
        bag_wdh = "10-12 Wdh."
    elif plan_age <= 15:
        if ft == "Gazelle" or reife_intern == "Spätentwickler":
            bag_text = "Power Bag 8-10 kg"
        else:
            bag_text = "Power Bag 10-13 kg"
        bag_wdh = "12-15 Wdh."
    elif plan_age <= 17:
        if ft == "Gazelle":
            bag_text = "Power Bag 10-13 kg"
        else:
            bag_text = "Power Bag 12-15 kg"
        bag_wdh = "12-15 Wdh."
    else:
        if gewicht < 70 or ft == "Gazelle":
            bag_text = "Power Bag 12-16 kg"
        else:
            bag_text = "Power Bag 15-17 kg"
        bag_wdh = "12-15 Wdh."

    if band == "U11":
        bag_text = "Körpergewicht; keine Powerbag-Zusatzlast hinterlegt"
    elif band == "U13":
        bag_text = "Powerbag 8–10 kg" if geschlecht_wahl == "Weiblich" else "Powerbag 8–12 kg"
    elif band == "U15":
        bag_text = "Powerbag 8–12 kg" if geschlecht_wahl == "Weiblich" else "Powerbag 12–15 kg; bei Bedarf z. B. 10 kg"
    if band in ("U17","U20","U23","MASTER"):
        stocks={"U17":("8–10","15"),"U20":("8–12","17"),"U23":("10–15","20"),"MASTER":("10–15","20")}
        bag_text="Powerbag "+stocks[band][0 if geschlecht_wahl=="Weiblich" else 1]+" kg"
    if bag_override > 0:
        bag_text = f"Powerbag {bag_override:g} kg (individuelle Trainerfestlegung)"

    bag_exercise="Front Squat Jumps / Anreiß-Sprünge"

    # Griffbälle für Umsatz/Crunch
    if plan_age <= 13:
        gb_last_kg = 3
    elif plan_age <= 15:
        gb_last_kg = 5 if ft in ["Kraft", "Schnelligkeit (Sprint)"] else 3
    elif plan_age <= 17:
        gb_last_kg = 7 if ft == "Kraft" else 5
    else:
        gb_last_kg = 9 if ft == "Kraft" and gewicht >= 75 else 7

    # Eigenständige Hauptübung: keine Kopplung an die Auswahl der Sprungausführung.
    hex_text = kreuzheben_load(band, kreuzheben_last)
    strength_exercise = "Kreuzhebe-Streckung"
    if band == "U13" or (band == "U15" and geschlecht_wahl == "Weiblich"):
        strength_exercise = "Anreiß-Jumps / Anreiß-Sprünge (Powerbag)"
        hex_text = ("Powerbag 8–10 kg" if geschlecht_wahl == "Weiblich" else "Powerbag 8–12 kg") if band == "U13" else "Powerbag 10–15 kg"
    elif band not in ["U11", "U13"] and not kreuzheben_last:
        ranges = {"U15":("", "30–45"), "U17":("30–40", "40–60"), "U20":("40–50", "50–70"), "U23":("40–60", "60–85"), "MASTER":("40–60", "60–85")}
        hex_text = "Hex Bar " + ranges[band][0 if geschlecht_wahl == "Weiblich" else 1] + " kg (Lastbereich)"

    # Hürden-Tiefsprünge
    if plan_age <= 13:
        tief_hoehe = "30-38 cm"
        tief_kh = "ohne ZL"
    elif plan_age <= 15:
        tief_hoehe = "38-45 cm"
        tief_kh = "ohne ZL bis 2x 1 kg KH"
    elif plan_age <= 17:
        tief_hoehe = "45 cm (Abstand 4,5 Fuß)"
        tief_kh = "2x 1 kg bis 2x 2 kg KH (Spitze 2x 3 kg)"
    else:
        tief_hoehe = "45-55 cm (Abstand 4-5 Fuß)"
        tief_kh = "2x 2 kg bis 2x 4 kg KH"

    st.info("Doc Athletic Trainerplanung: vom Niederen zum Höheren, Links-rechts-Symmetrie und Anpassung an das Belastungsempfinden. Lasten, Umfänge und Einheitsziel vor der Anwendung individuell prüfen.")
    html_matrices = ""
    rendered_plans = {}

    base_bag_text,base_hex_text=bag_text,hex_text
    base_strength_exercise=strength_exercise
    for te_num in te_liste:
        planned_phase,effective_phase=phase_status(phase_config,band,te_num)
        bag_text,hex_text=base_bag_text,base_hex_text
        bag_exercise="Front Squat Jumps / Anreiß-Sprünge"
        strength_exercise=base_strength_exercise
        if effective_phase=="Zyklus abgeschlossen":
            html_matrix=f'<div class="druck-block"><h3>TRAININGSMATRIX - EINHEIT: TE {te_num}</h3><p>Außerhalb des konfigurierten Makrozyklus. Neuen Zyklus planen oder Phasenlängen ändern. Gespeicherte Soll-/Ist-Protokolle bleiben unten abrufbar.</p></div>'
            rendered_plans[te_num]=html_matrix;html_matrices+=html_matrix
            continue
        if effective_phase in ("Grundlast","Jumps","Sprünge"):
            bag_exercise=phase_exercise_label("front_squat",effective_phase)
            kind="anreiss" if band=="U15" and geschlecht_wahl=="Weiblich" else "kreuzheben"
            strength_exercise=phase_exercise_label(kind,effective_phase)
            chosen=phase_load(phase_config,"front_squat",band,te_num)
            if chosen:bag_text="Powerbag "+chosen
            chosen=phase_load(phase_config,kind,band,te_num)
            if chosen:hex_text=("Powerbag " if kind=="anreiss" else "Hex Bar ")+chosen

        week, day, short_day = unit_context(te_num, einheiten, startwoche, role)
        # Existing 14-block sequence is keyed to TE, never to calendar week.
        woche = te_num
        abc_dist = vorgaben["start_m"] + ((week - 1 if progression else 0) * abc_step)
        warmup = warmup_text(band, te_num)
        bag_count = weekly_reps(bag_start, week, 20 if capacity else 15, progression, rep_step)
        bag_wdh = "8–6–5 Wdh. (3 Sätze)" if short_day else f"{bag_count} Wdh. je Satz"
        day_label = "Vollständige Komplexeinheit · 1 TE/Woche" if einheiten == 1 else ("Neuromuskulär / vor dem Spiel" if short_day else "Haupttag")
        split_main = einheiten == 2 and not short_day
        main_sets = str(org_config.get("main_sets", 4)) if split_main else "3"
        current_unit = "Basis" if einheiten == 1 else "TE2" if short_day else "TE1"
        timing = weekly_timing(aktive_kategorie, band, einheiten, current_unit)
        extra_rows = ""
        m_sprint_row = ""
        for m_row in m_training_rows(m_config, aktive_kategorie, band, te_num, einheiten, short_day):
            cells = [m_row["Block"], m_row["Trainingsmittel"], m_row["Sätze"],
                     m_row["Wdh_oder_Strecke"], m_row["Zusatzlast"],
                     m_row["Intensität"] + "; " + m_row["Fokus"], m_row["Pause"]]
            m_sprint_row += '<tr style="background:#e8f4f0">' + ''.join(
                '<td style="padding:6px;border:1px solid #aaa">'+escape(cell)+'</td>' for cell in cells) + '</tr>'

        if short_day:
            extra_rows += exercise_row("Komplextransfer: Hürdensprünge / Hürden-Steigesprung / kurze Sprints", "3", "5–8 Wiederholungen; Techniktransfer", "Körpergewicht", "Neuromuskulärer Erinnerungsreiz")
        else:
            burpee_rep = str(weekly_reps(burpee_start,week,100,progression,rep_step)) + " Wdh." if burpees_ok else "Startwert noch bestätigen"
            extra_rows += exercise_row("Burpees / Liegestützsprünge mit Strecksprung", "3", burpee_rep, "Powerbar 2–3 kg gesamt: ab U15 noch bestätigen" if plan_age >= 14 else "Zusatzlast noch individuell bestätigen", f"+{rep_step} Wdh./Woche bei Freigabe")
            paired = weekly_reps(cheer_start,week,100,progression,rep_step) if cheer_start else 0
            pair_text = f"{paired} links + {paired} rechts = {paired*2} gesamt" if paired else "Start je Seite noch festlegen"
            extra_rows += exercise_row("Cheerleading: beidbeinige Fußgelenksprünge, Arme wechselseitig", "3", pair_text, cheer_load(band,geschlecht_wahl), f"+{rep_step} je Seite / Woche")
            paired = weekly_reps(single_start,week,100,progression,rep_step) if single_start else 0
            pair_text = f"{paired} links + {paired} rechts = {paired*2} gesamt" if paired else "Start je Bein noch festlegen"
            extra_rows += exercise_row("Leg Speed Curler einbeinig", "3", pair_text, "Gerätespezifischer Widerstand: aus dokumentierter Ist-Einheit in Sollplan übernehmen", f"+{rep_step} je Bein / Woche")
            bilateral = str(weekly_reps(bilateral_start,week,100,progression,rep_step)) + " Wdh." if bilateral_start else "Start noch festlegen"
            extra_rows += exercise_row("Leg Speed Curler beidbeinig", "3", bilateral, "Gerätespezifischer Widerstand: aus dokumentierter Ist-Einheit in Sollplan übernehmen", f"+{rep_step} gemeinsame Wdh./Woche")


        if plan_age <= 13:
            abc_last_str = "1,5-2,0 kg Power Bar über Kopf"
        elif plan_age <= 15:
            abc_last_str = "2,0 kg Power Bar über Kopf" if ft == "Gazelle" else "2,0-3,0 kg Power Bar über Kopf"
        elif plan_age <= 17:
            if woche in [1, 2]:
                abc_last_str = "Ohne Stange (Fokus Bahnung/Frequenz)"
            else:
                abc_last_str = "2,0-3,0 kg Power Bar über Kopf" if gewicht < 70 else "3,0-4,0 kg Power Bar über Kopf"
        else:
            abc_last_str = "2,0-3,0 kg Power Bar über Kopf" if gewicht < 70 else "3,0-4,0 kg Power Bar über Kopf"

        pause_komplex = "Stationswechsel bis 60 s; Serienpause separat"

        if plan_age <= 15:
            if woche in [1, 2]:
                tl_pos = "nach_komplex"
                tl_text = "6 x 100m TL (75-80%)"
                tl_pause = "50m Gehpause"
            elif woche in [3, 4]:
                tl_pos = "nach_komplex"
                tl_text = "4 x 150m + 2 x 100m TL (> 75%)"
                tl_pause = "50m Gehpause"
            elif woche in [5, 6]:
                tl_pos = "nach_komplex"
                tl_text = "2 x 300m + 2 x 200m + 2 x 150m TL (Absteigend)"
                tl_pause = "100m Gehpause"
            elif woche == 7:
                tl_pos = "nach_komplex"
                tl_text = "2 x 400m + 2 x 300m + 2 x 200m TL (Absteigend)"
                tl_pause = "100m Gehpause"
            elif woche in [8, 9, 10]:
                tl_pos = "vor_komplex"
                tl_text = "2 x 600m (Basis 60%) + 2 x 400m + 3 x 200m (GLA vorab)"
                tl_pause = "100m Gehpause (200m bei 50m GP)"
            elif woche == 11:
                tl_pos = "vor_komplex"
                tl_text = "3 x 600m TL (Richtwert 1:40 min) + 4 x 150m Speed"
                tl_pause = "100m Gehpause"
            elif woche == 12:
                tl_pos = "nach_komplex"
                tl_text = "Speed-Shuttle auf Kunstrasen: 4 x 55m Doppel-Shuttle + Antritte"
                tl_pause = "Staffelpause"
            elif woche == 13:
                tl_pos = "marathon"
                tl_text = "Athletik & Lauf-Marathon: 3 Runden à 400m TL (50%) + Parcours"
                tl_pause = "Im Kettenablauf"
            else:
                tl_pos = "nach_komplex"
                tl_text = "Abschlusstest: 60m Zeit + 250m Zeit + 600m Zeit (Maximal)"
                tl_pause = "Volle Erholung"

        elif plan_age <= 17:
            if woche in [1, 2]:
                tl_pos = "nach_komplex"
                tl_text = "6 x 100m Technik TL (80%) [Lauf-ABC ohne Stange]"
                tl_pause = "50m Gehpause"
            elif woche in [3, 4]:
                tl_pos = "nach_komplex"
                tl_text = "2 x 300m + 2 x 200m + 2 x 150m TL (Absteigend)"
                tl_pause = "100m Gehpause"
            elif woche in [5, 6]:
                tl_pos = "nach_komplex"
                tl_text = "1 x 500m + 1 x 400m + 2 x 300m + 2 x 200m (Absteigend 70-80%)"
                tl_pause = "100m Gehpause"
            elif woche == 7:
                tl_pos = "nach_komplex"
                tl_text = "2 x 550m + 2 x 350m TL (Kaskade > 65%)"
                tl_pause = "100m Gehpause"
            elif woche in [8, 9, 10]:
                tl_pos = "vor_komplex"
                tl_text = "GLA vorab: 600m, 600m, 500m, 500m (je 100m GP) vor Stationen"
                tl_pause = "100m Gehpause"
            elif woche == 11:
                tl_pos = "vor_komplex"
                tl_text = "GLA vorab: 1 x 700m Kappe + 2 x 500m + 3 x 150m Speed"
                tl_pause = "100m Gehpause"
            elif woche == 12:
                tl_pos = "nach_komplex"
                tl_text = "Witterungs-Speed: 12 x 40m Doppel-Shuttle mit 3 kg ZL"
                tl_pause = "5s Wende / Staffelpause"
            elif woche == 13:
                tl_pos = "marathon"
                tl_text = "Athletik- & Lauf-Marathon: 3x 400m Schleifen-Shuttle + Parcours"
                tl_pause = "Im Kettenablauf"
            else:
                tl_pos = "nach_komplex"
                tl_text = "Saison-Peak: 60m Sprint + 250m + 600m Test auf Zeit"
                tl_pause = "Volle Erholung"

        else:
            if woche in [1, 2]:
                tl_pos = "nach_komplex"
                tl_text = "6 x 100m Technik Sprintlauf (> 85%) direkt nach Station 1"
                tl_pause = "50-100m Gehpause"
            elif woche in [3, 4]:
                tl_pos = "nach_komplex"
                tl_text = "Komplextransfer: 2x 150m Sprint (>85%) + 1x 350m (>70%) + 1x 550m (70%)"
                tl_pause = "100m Gehpause"
            elif woche in [5, 6]:
                tl_pos = "nach_komplex"
                tl_text = "Absteigende Kaskade: 600m (60%) + 500m (70%) + 400m (70%) + 300m (80%)"
                tl_pause = "100m langsame Gehpause"
            elif woche == 7:
                tl_pos = "nach_komplex"
                tl_text = "KZA Kaskade: 2x 450m + 2x 550m (> 60%) + 100m Gehpause"
                tl_pause = "100m Gehpause"
            elif woche in [8, 9, 10]:
                tl_pos = "vor_komplex"
                tl_text = "GLA vorab: 800m (unter 3:15 min) + 600m, 600m (unter 2:30 min) + 500m vor Stationen"
                tl_pause = "100m Gehpause"
            elif woche == 11:
                tl_pos = "vor_komplex"
                tl_text = "GLA vorab: 800m Basis + 600m, 600m + 500m, 500m (je 100m GP)"
                tl_pause = "100m Gehpause"
            elif woche == 12:
                tl_pos = "nach_komplex"
                tl_text = "Staffel-Ausdauer Kunstrasen: 4x 220m (80%) + 5x 220m (90%)"
                tl_pause = "Staffelpause"
            elif woche == 13:
                tl_pos = "marathon"
                tl_text = "Athletik- & Lauf-Marathon: 3x 400m TL (>50%) + Tartan-Halbmond Parcours"
                tl_pause = "Im Kettenablauf"
            else:
                tl_pos = "nach_komplex"
                tl_text = "Abschlusstest: 60m Sprint + 250m Sprint + 600m Test auf Zeit"
                tl_pause = "Volle Erholung"

        if short_day:
            tl_pos = "nach_komplex"
            tl_text = "Kurze Antritte / Sprints nach dem Komplex; Umfang individuell, kein laktazider Laufblock"
            tl_pause = "Erholung nach Trainerfestlegung"
        test_note = (f"Testauswertung (keine Laufvorgabe): {test_distance} m: {test_seconds / (test_percent / 100):.1f} s bei {test_percent}% der gemessenen Testgeschwindigkeit"
                     if test_seconds > 0 else "Tempolauf-Zielzeit: Test derselben Distanz noch eingeben")
        phase_label = "Phase 1: Komplextraining: Kraft und anschließende Sprünge/Sprints" if woche <= 7 else "Phase 2: Laktazide Vorab-Ermüdung" if woche <= 11 else "Phase 3: Marathon & Zuspitzung"
        
        if short_day:
            phase_label = "Neuromuskulärer Erinnerungsreiz"
        row_gla_vorab = ""
        if tl_pos == "vor_komplex":
            row_gla_vorab = f'<tr style="background-color: #FCE4D6;"><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold; color: #C00000;">Block 1: GLA Vorab</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{tl_text}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">Serie</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Kaskade vor Kraft</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">60-70% Vmax</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{tl_pause}</td></tr>'

        row_tl_transfer = ""
        if tl_pos in ["nach_komplex", "marathon"]:
            row_tl_transfer = f'<tr style="background-color: #FCE4D6;"><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Block 2: Lauf / Transfer</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{tl_text}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Variabel</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Direct-Transfer</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{escape("Kurz und hochwertig" if short_day else "Individuelles Trainingsziel")}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{tl_pause}</td></tr>'

        if effective_phase in ("Grundlast", "Jumps", "Sprünge"):
            phase_label = f"{effective_phase} · vorgesehene Phase: {planned_phase}"
        strength_intensity = "Technisch kontrolliert" if effective_phase == "Grundlast" else "Explosiv bei sauberer Technik"
        html_matrix = f'''<meta charset="utf-8">
<div class="druck-block" style="background-color: #111111; color: #ffffff; border: 2px solid #45a29e; border-radius: 8px; padding: 20px; margin-top: 20px; font-family: Arial, sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #66fcf1; padding-bottom: 5px;">
<h3 style="margin: 0; color: #66fcf1 !important;">TRAININGSMATRIX - EINHEIT: TE {woche}</h3>
<span style="color: #ffb703; font-weight: bold; font-size: 14px;">{phase_label}</span>
</div>
<p style="color: #ffffff !important; font-size: 14px; margin-top: 8px;"><strong>Makrozyklus:</strong> {escape(aktuelle_daten.get("aktiver_makrozyklus", "Bestand"))} | <strong>Athlet:</strong> {escape(ziel)} ({gewicht} kg) | <strong>Woche:</strong> {week}, Einheit {day} | <strong>Ziel:</strong> {day_label} | <strong>Phase:</strong> {effective_phase} (vorgesehen: {planned_phase}) | <strong>Lauf-ABC Last:</strong> {abc_last_str}</p>
<p>{escape(test_note)}</p>
<table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; color: #000000; border: 1px solid #7F7F7F;">
<thead>
<tr style="background-color: #1F4E78; color: #FFFFFF; font-weight: bold;">
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 16%;">Block / Phase</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 26%;">Trainingsmittel / Übung</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 7%; text-align: center;">Sätze</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 17%;">Wdh. / Distanz</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 16%;">Hardware / Zusatzlast</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 10%;">Intensität</th>
<th style="padding: 8px; border: 1px solid #7F7F7F; width: 8%; text-align: center;">Pause</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #FFF2CC;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Erwärmung</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Einlaufen / Aktivierung</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">1</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{escape(warmup)}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Einlaufen</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">Trinkp.</td>
</tr>
<tr style="background-color: #DDEBF7;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Block 1: ABC</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Kniehebelauf & Anfersen / Streckbein</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">2</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{abc_dist:.1f}m hin / STL zurück</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{abc_last_str}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">>80% frequent</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">2s</td>
</tr>
{row_gla_vorab}
<tr style="background-color: #BDD7EE;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Komplex: Hürden</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Hürden-Tiefsprünge (Reaktiv / DVZ)</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"6–8 Hürden" if short_day else "8–12 Hürden (Trainerbasis)"} ({tief_hoehe})</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{tief_kh}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Maximal explosiv</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">3 Min. SP</td>
</tr>
<tr style="background-color: #FCE4D6;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Eigenständige Kraft-Hauptübung</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{strength_exercise}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{"3" if short_day else "3–4 (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"8–6–5 Wdh." if short_day else "8–12 Wdh. (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{hex_text}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{strength_intensity}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{pause_komplex}</td>
</tr>
<tr style="background-color: #FCE4D6;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Komplex: Bags</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{bag_exercise}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{bag_wdh}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{bag_text}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{strength_intensity}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">Stationswechsel bis 60 s</td>
</tr>
<tr style="background-color: #FCE4D6;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Komplex: Bälle</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Umsatz / Ausstoß-Jumps & Crunches</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"5–8 Wdh." if short_day else "12–15 Wdh. (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Griffball {gb_last_kg} kg</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Max. Schnellkraft</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">60s</td>
</tr>
{extra_rows}
{m_sprint_row}
{row_tl_transfer}
<tr style="background-color: #E2EFDA;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Block 3: Rumpf/TRX</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Zug im Schrägliegehang am TRX / Barren</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"5–8 Wdh." if short_day else "12–15 Wdh. (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Körpergewicht</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Submaximal</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">60s</td>
</tr>
<tr style="background-color: #F2F2F2;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Cool-Down</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Auslaufen & Statische Tonus-Regulation</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">1</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">300-400 m</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Sehr locker</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">–</td>
</tr>
</tbody>
</table>
</div>'''
        html_matrix = organize_multisport_html(html_matrix, einheiten, short_day, main_sets, aktive_kategorie, band, org_config, timing)
        rendered_plans[te_num] = html_matrix
        html_matrices += html_matrix

    if modus == "Einzelathlet / Einzelathletin" and ziel in aktive_athleten_db:
        protocol_te = st.selectbox("Einheit für Soll-/Ist-Protokoll", list(te_liste), key=key_for("protocol_te"))
        unit_workflow(aktuelle_daten, aktive_kategorie, ziel, protocol_te, plan_as_text(rendered_plans[protocol_te]), key_for, guest, weekly_timing(aktive_kategorie, band, einheiten, "TE2" if unit_context(protocol_te, einheiten, startwoche, role)[2] else "TE1"))
    st.markdown(html_matrices, unsafe_allow_html=True)
    st.markdown("---")

    st.download_button(
        label="💾 Trainingsplan und Tempotabelle herunterladen",
        data="<!doctype html><html lang=\"de\"><head><meta charset=\"utf-8\"><title>Doc Athletic Train Smart Evolution Software – Trainingsplan</title><style>body{font-family:Arial,sans-serif}table{border-collapse:collapse}th,td{padding:6px;border:1px solid #aaa}@media print{@page{size:A4 landscape;margin:10mm}.druck-block{break-before:page;background:#fff!important;color:#111!important;border:0!important}.druck-block h3,.druck-block p,.druck-block span{color:#111!important}}</style></head><body>" + "<h1>Doc Athletic Train Smart Evolution Software 105 · Trainingsentwurf</h1><p>Trainerplanung nach individuellen Referenzen und Belastungsverträglichkeit. Berechnete Richtwerte sind Orientierungshilfen.</p><h2>Tempotabelle 50–800 m</h2><p>Prozentwerte der mittleren Referenzgeschwindigkeit. Zwischenwerte und ausdrücklich aktivierte Fortsetzungen sind als Richtwerte gekennzeichnet. Einlaufzeiten bleiben separat.</p>" + pd.DataFrame(tempo_data).to_html(index=False, escape=True) + html_matrices + "</body></html>",
        file_name=f"Doc_Athletic_Trainingsplan_{ziel.replace(' ', '_')}.html",
        mime="text/html; charset=utf-8"
    )

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        st.markdown("""<div style="text-align: center; border: 2px solid #45a29e; border-radius: 8px; padding: 15px; background-color: #111111;">
<h2 style="color: #66fcf1 !important; margin-bottom: 5px; font-family: Arial, sans-serif;">Aufgeben gilt nicht!</h2>
<p style="color: #ffb703 !important; font-size: 16px; font-weight: bold; margin: 8px 0;">>>Das, was du fühlst, ist nicht das, was du kannst.<<</p>
<p style="color: #ffffff !important; font-size: 13px; letter-spacing: 1px; margin-top: 5px;">DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE 105</p>
</div>""", unsafe_allow_html=True)
        lade_bild(["Foto.jpg", "Foto.JPG", "foto.jpg", "foto.JPG", "Foto.jpeg", "foto.jpeg", "Foto.png", "foto.png"], use_col=True)
