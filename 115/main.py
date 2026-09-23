# ============================================================================
# DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE - FUSSBALL (Version 115)
# ChatGPT überarbeitet auf Grundlage 23.8.5; Modul 1
# Überarbeitet: Soll/Ist, 25 Quellenpläne, Folgeempfehlungen, Makrozyklen, Sprungtest-Verlauf
# Stand: 23.09.2026 – Stammdatenimport XLSX/ODS/CSV, variable Strecken und Wendezuschlag
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
import csv
import io
import re
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile

st.set_page_config(page_title="Doc Athletic – Fußball · 115", layout="wide", initial_sidebar_state="expanded")

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
DATABASE_URL = setting("DOC_ATHLETIC_115_DATABASE_URL")
if TRAINER_CODE and GAST_CODE and TRAINER_CODE == GAST_CODE:
    st.error("Trainer- und Gastcode müssen unterschiedlich sein.")
    st.stop()

# SQLite writes are transactional; revisions prevent stale sessions overwriting data.
# The hosting platform must retain this directory. JSON downloads are portable backups.
DATA_DIR = Path(os.environ.get("DOC_ATHLETIC_115_DATA_DIR", str(Path(__file__).resolve().parent / "data_115")))
DB_FILE = DATA_DIR / "doc_athletic.sqlite3"
KADER_DATEI = DATA_DIR / "kader_db.json"
VALID_PROFILES = {'Fussball_U13', 'Leichtathletik_MASTER_w', 'Fussball_U23_m', 'Fussball_U23_w', 'Fussball_MASTER_w', 'Fussball_U20_m', 'Leichtathletik_MASTER_m', 'Leichtathletik_U17_m', 'Fussball_U17_w', 'Fussball_U15_w', 'Leichtathletik_U11', 'Leichtathletik_U15', 'Leichtathletik_U17_w', 'Leichtathletik_U20_w', 'Fussball_U15_m', 'Fussball_U17_m', 'Fussball_U20_w', 'Leichtathletik_U23_w', 'Fussball_MASTER_m', 'Leichtathletik_U20_m', 'Leichtathletik_U13', 'Leichtathletik_U23_m', 'Fussball_U11'}
DEFAULT_KADER = {"Fussball": {}, "Leichtathletik": {}}

# Existing storage sections remain readable. Both are shown in one roster;
# no automatic name-based merge can overwrite an older athlete or history.
FOCUS_LABELS = {
    "komplex": "Fußball 1 – Komplextraining",
    "speed_jump": "Fußball 2 – Speed and Jump",
}
BUILD_STAND = "23.09.2026 · Kader- und Tabellenimport · Stand 115.3"


# Version 115: agreed working values; saved plans remain immutable until edited.
PARTNER_PAUSE = "Lohnende Pause durch Partnerwechsel"
PARTNER_ORGANIZATION = (
    "Staffelbetrieb mit mehreren Linien bzw. Übungsreihen, bei Gewichtsstangen "
    "mindestens zwei bis drei Linien; die Partner wechseln nach jeder Ausführung."
)
ABC_115 = {
    "U11": ((10., 20., "0"), (10., 20., "0")),
    "U13": ((15., 25., "0"), (15., 25., "0")),
    "U15": ((20., 30., "2"), (20., 30., "2")),
    "U17": ((25., 40., "3"), (20., 35., "3")),
    "U20": ((30., 50., "3"), (25., 40., "3")),
    "U23": ((30., 60., "3–4"), (25., 45., "3")),
    "MASTER": ((30., 60., "3–4"), (25., 45., "3")),
}
HURDLE_FORMS = ("M-Hürdensprints", "Hürden-Steigesprünge", "Hürden-Tiefsprünge / CMJ", "Ohne Hürden")
M_HURDLE_EDGES = {"U11": (12., 15.), "U13": (15., 18.), "U15": (15., 20.),
                  "U17": (17., 20.), "U20": (20., 25.), "U23": (20., 28.), "MASTER": (20., 28.)}
M_HURDLE_HEIGHTS = {"U11": 25, "U13": 30, "U15": 38, "U17": 45, "U20": 45, "U23": 45, "MASTER": 45}
U11_DUMBBELLS = {"Cheerleading": 1, "Umsatz-/Ausstoßsprünge auf der Stelle": 1,
                 "Squat-/Stoßsprünge": 1, "Candle Jumps": 1, "Burpees mit Kurzhanteln": 1,
                 "Burpees ohne Kurzhanteln": 0, "Kreuzhebesprünge auf der Stelle": 2,
                 "Front Squat Jumps": 2}


def abc_values(band, gender, week, progression, start=None):
    initial, cap, load = ABC_115[band][gender == "Weiblich"]
    if band == "U11" and start is not None:
        initial = max(10., min(15., float(start)))
    distance = min(cap, initial + (max(0, week - 1) * 2 if progression else 0))
    return distance, load


def abc_rows_115(band, gender, week, progression, start=None):
    distance, load = abc_values(band, gender, week, progression, start)
    equipment = ("Ohne Stange" if load == "0" else
                 f"Stange {load} kg gesamt; Arme gestreckt über Kopf, Griffbreite ca. 1,5 × Schulterbreite; auch beim Rückweg")
    rows = []
    for name in ("Kniehebelauf", "Anfersen", "Seitlicher Nachstellschritt", "Hopserlauf"):
        direction = "; je einmal in beide Richtungen" if name == "Seitlicher Nachstellschritt" else ""
        rows.append(["Block 1: ABC", name, "2 Bahnen insgesamt" + direction,
                     f"Je {distance:g} m hin + {distance:g} m Beschleunigung zurück; {4*distance:g} m insgesamt",
                     equipment, "Kontrollierter Geschwindigkeitsaufbau auf dem Rückweg", PARTNER_PAUSE])
    return rows


def hurdle_defaults():
    return {"forms": [HURDLE_FORMS[i % 3] for i in range(28)], "overrides": {}}


def hurdle_plan(config, band, te):
    config = config or hurdle_defaults()
    forms = config.get("forms", hurdle_defaults()["forms"])
    form = forms[te - 1]
    occurrence = forms[:te].count(form)
    stage = min(occurrence - 1, 5)
    if form == HURDLE_FORMS[0]:
        # First increase hurdle count, then spacing. Intermediate stages are editable.
        hurdles, spacing = ((2, 7.), (3, 7.), (4, 7.), (4, 7.5), (4, 8.), (4, 8.))[stage]
        lo, hi = M_HURDLE_EDGES[band]
        edge = round(lo + (hi - lo) * min(occurrence - 1, 2) / 2, 1)
        row = dict(sets=3, hurdles=hurdles, spacing_ft=f"{spacing:g}",
                   height_cm=str(M_HURDLE_HEIGHTS[band]), edge_m=edge)
    else:
        # 18 -> 24 -> 30; later example stages preserve increasing total volume.
        sets, hurdles = ((3, 6), (4, 6), (5, 6), (4, 8), (4, 10), (4, 12))[stage]
        # Keep existing height corridors as corridors; do not copy the M height table.
        height = {"U11": "30", "U13": "30–38", "U15": "38–45", "U17": "45",
                  "U20": "45–55", "U23": "45–55", "MASTER": "45–55"}[band]
        if form == HURDLE_FORMS[2]:
            if band == "U11":
                height = "30" if occurrence < 3 else "38"
            spacing = {"U11": "4", "U17": "4,5", "U20": "4–5", "U23": "4–5", "MASTER": "4–5"}.get(band, "nach Übungsaufbau")
        else:
            spacing = str((7, 7, 8, 8, 9, 9)[stage])
        row = dict(sets=sets, hurdles=hurdles, spacing_ft=spacing, height_cm=height, edge_m=0.)
    override = config.get("overrides", {}).get(str(te), {})
    if override.get("form") == form:
        row.update({k: override[k] for k in row if k in override})
    # Explicit fixed form-specific values have precedence over old saved overrides.
    if form == HURDLE_FORMS[0]:
        row["height_cm"] = str(M_HURDLE_HEIGHTS[band])
    if form == HURDLE_FORMS[2] and band == "U11":
        row.update(height_cm="30" if occurrence < 3 else "38", spacing_ft="4")
    return dict(row, form=form, occurrence=occurrence)


def validate_hurdles(config, band):
    if not isinstance(config, dict) or set(config) - {"forms", "overrides"}:
        raise ValueError("Hürdenplanung prüfen.")
    forms = config.get("forms", hurdle_defaults()["forms"])
    if not isinstance(forms, list) or len(forms) != 28 or any(x not in HURDLE_FORMS for x in forms):
        raise ValueError("Hürdenfolge benötigt 28 gültige Einträge.")
    overrides = config.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("Individuelle Hürdenvorgaben prüfen.")
    for key, row in overrides.items():
        if key not in [str(i) for i in range(1, 29)] or not isinstance(row, dict):
            raise ValueError("Einheit der Hürdenvorgabe prüfen.")
        if set(row) - {"form", "sets", "hurdles", "spacing_ft", "height_cm", "edge_m"} or row.get("form") not in HURDLE_FORMS:
            raise ValueError("Hürdenform prüfen.")
        for field in ("height_cm", "spacing_ft"):
            if field in row and (not isinstance(row[field], str) or not 1 <= len(row[field]) <= 60):
                raise ValueError("Hürdenhöhe oder Abstand prüfen.")
        for field in ("sets", "hurdles"):
            if field in row and type(row[field]) is not int:
                raise ValueError("Durchgänge und Hürdenzahl müssen ganze Zahlen sein.")
        edge = row.get("edge_m", 0.)
        if type(edge) not in (int, float) or not math.isfinite(edge):
            raise ValueError("Kantenlänge prüfen.")
    for te in range(1, 29):
        row = hurdle_plan(config, band, te)
        if not 1 <= row["sets"] <= 10:
            raise ValueError("Durchgänge müssen zwischen 1 und 10 liegen.")
        if row["form"] == HURDLE_FORMS[0]:
            lo, hi = M_HURDLE_EDGES[band]
            if not lo <= row["edge_m"] <= hi or row["hurdles"] not in (2, 3, 4) or row["spacing_ft"] not in ("7", "7.5", "8"):
                raise ValueError("M-Hürden: Kante, Hürdenzahl oder Abstand außerhalb des vereinbarten Bereichs.")
        elif row["form"] != HURDLE_FORMS[3]:
            if row["hurdles"] not in (6, 8, 10, 12):
                raise ValueError("Für die Hürdenreihe 6, 8, 10 oder 12 Hürden wählen.")
            if row["form"] == HURDLE_FORMS[1] and row["spacing_ft"] not in ("7", "8", "9"):
                raise ValueError("Steigesprünge: 7, 8 oder 9 Fuß Abstand wählen.")
    return deepcopy(config)


def hurdle_ui(saved, band, key, disabled=False):
    draft_key = key + "draft"
    if draft_key not in st.session_state:
        st.session_state[draft_key] = {**hurdle_defaults(), **deepcopy(saved or {})}
    config = deepcopy(st.session_state[draft_key])
    config = validate_hurdles(config, band)
    with st.expander("Speed and Jump: Hürdenwechsel und Aufbau", expanded=False):
        st.caption("M-Hürdensprints → Hürden-Steigesprünge → Hürden-Tiefsprünge / CMJ. Der Aufbau zählt die Einsätze jeder Form, unabhängig von Kalenderwochen.")
        st.caption(PARTNER_PAUSE + ". " + PARTNER_ORGANIZATION)
        te = st.number_input("Hürdenplanung: Einheit", 1, 28, 1, key=key+"te")
        form = st.selectbox("Hürdenform dieser Einheit", HURDLE_FORMS,
                            index=HURDLE_FORMS.index(config["forms"][te-1]), key=key+str(te)+"form", disabled=disabled)
        config["forms"][te-1] = form
        row = hurdle_plan(config, band, te)
        if form != HURDLE_FORMS[3]:
            p = key+str(te)+form
            st.caption(f"Einsatz {row['occurrence']} dieser Form. Die folgenden Werte gehören zur gesamten Einheit; seitenspezifische Durchgänge gelten jeweils links und rechts.")
            cols = st.columns(3)
            row["sets"] = cols[0].number_input("Hürden: Durchgänge je Ausführung / Seite", 1, 10, row["sets"], key=p+"sets", disabled=disabled)
            choices = [2, 3, 4] if form == HURDLE_FORMS[0] else [6, 8, 10, 12]
            row["hurdles"] = cols[1].selectbox("Hürden je Kante / Reihe", choices, index=choices.index(row["hurdles"]), key=p+"hurdles", disabled=disabled)
            fixed_height = form == HURDLE_FORMS[0] or (form == HURDLE_FORMS[2] and band == "U11")
            row["height_cm"] = cols[2].text_input("Hürdenhöhe (cm)", row["height_cm"], key=p+"height", disabled=disabled or fixed_height)
            if form == HURDLE_FORMS[0]:
                lo, hi = M_HURDLE_EDGES[band]
                row["edge_m"] = st.number_input("M-Hürden: Kantenlänge (m)", lo, hi, float(row["edge_m"]), .5, key=p+"edge", disabled=disabled)
                choices = ["7", "7.5", "8"]
                row["spacing_ft"] = st.selectbox("M-Hürden: Abstand (Fuß)", choices, index=choices.index(row["spacing_ft"]), key=p+"spacing", disabled=disabled)
            elif form == HURDLE_FORMS[1]:
                choices = ["7", "8", "9"]
                row["spacing_ft"] = st.selectbox("Steigesprünge: Abstand (Fuß)", choices, index=choices.index(row["spacing_ft"]), key=p+"spacing", disabled=disabled)
            else:
                row["spacing_ft"] = st.text_input("Tiefsprünge: Abstand (Fuß)", row["spacing_ft"], key=p+"spacing", disabled=disabled or band == "U11")
            config["overrides"][str(te)] = {k: v for k, v in row.items() if k != "occurrence"}
        preview = []
        for current in range(1, 29):
            r = hurdle_plan(config, band, current)
            count = r["sets"] * r["hurdles"]
            total = count * (8 if r["form"] == HURDLE_FORMS[0] else 2 if r["form"] == HURDLE_FORMS[1] else 1)
            preview.append({"TE": current, "Form": r["form"], "Einsatz": r["occurrence"],
                            "Durchgänge je Seite / Ausführung": r["sets"] if r["form"] != HURDLE_FORMS[3] else 0,
                            "Hürden je Kante / Reihe": r["hurdles"] if r["form"] != HURDLE_FORMS[3] else 0,
                            "Überquerungen gesamt": total if r["form"] != HURDLE_FORMS[3] else 0})
        st.dataframe(pd.DataFrame(preview), hide_index=True)
        st.caption("Arbeitsfolge für die gerade Reihe: 3×6 → 4×6 → 5×6; danach als anpassbare Vorlage 4×8 → 4×10 → 4×12. M-Form: zunächst 2 → 3 → 4 Hürden, anschließend größere Abstände. Ein Fuß entspricht hier 30 cm.")
        if band == "U11":
            st.caption("U11: Hürdensprünge ohne Kurzhanteln. Steigesprünge beginnen bei 30 cm; die feste Höhenfolge 30/30/38 cm gilt für Tiefsprünge.")
            st.dataframe(pd.DataFrame([{"Ergänzende Übung": name, "kg je Kurzhantel": kg} for name, kg in U11_DUMBBELLS.items()]), hide_index=True)
    config = validate_hurdles(config, band)
    st.session_state[draft_key] = deepcopy(config)
    return config


def hurdle_rows_115(config, band, te):
    r = hurdle_plan(config, band, te)
    form, sets, hurdles = r["form"], r["sets"], r["hurdles"]
    if form == HURDLE_FORMS[3]:
        return []
    equipment = f"Hürden {r['height_cm']} cm; Abstand {r['spacing_ft']} Fuß"
    try:
        meters = float(r["spacing_ft"].replace(",", ".")) * .3
        equipment += f" ({meters:.2f} m)"
    except ValueError:
        pass
    if form == HURDLE_FORMS[0]:
        per_m = 4 * hurdles
        return [["Speed: Hürdenumfang je Einheit", form, f"{sets} vollständige M je Seite; {2*sets} insgesamt",
                 f"4 Kanten à {r['edge_m']:g} m; {hurdles} Hürden je Kante; {per_m} Überquerungen je M; "
                 f"{2*sets*per_m} Überquerungen / {2*sets*4*r['edge_m']:g} m insgesamt",
                 equipment + "; ohne Zusatzlast",
                 "Zwei spiegelbildliche M, je fünf ca. 1 m hohe Eckstangen. M-Seite benennt das Schwungbein. Nächster Start an der nächsten Eckstange.", PARTNER_PAUSE]]
    result = []
    for side in ("links", "rechts") if form == HURDLE_FORMS[1] else ("beidbeinig",):
        result.append(["Speed: Hürdenumfang je Einheit", form + " · " + side, f"{sets} Durchgänge {side}",
                       f"{sets} × {hurdles} = {sets*hurdles} Überquerungen {side}; anschließend Beschleunigung zurück",
                       equipment + "; ohne Kurzhanteln",
                       "Fortlaufende Fuß-Knie-Hüftstreckung; " + ("jeder Durchgang vollständig auf derselben Seite" if side != "beidbeinig" else "abfangend und überwindend über Hürden"),
                       PARTNER_PAUSE])
    return result


def rows_html(rows):
    return ''.join('<tr>'+''.join('<td>'+escape(str(value))+'</td>' for value in row)+'</tr>' for row in rows)


def legacy_focus(record):
    return "speed_jump" if record.get("profil", "").startswith("Leichtathletik_") else "komplex"


def roster_options(kader):
    return [(sport, name) for sport in ("Fussball", "Leichtathletik") for name in kader[sport]]


def roster_label(identity, kader):
    sport, name = identity
    duplicate = sum(name in athletes for athletes in kader.values()) > 1
    if duplicate:
        return name + (" (Fußball-Bestand)" if sport == "Fussball" else " (Altbestand Speed and Jump)")
    return name


def football_profile(profile, gender="Männlich"):
    band = profile.split("_")[1]
    suffix = "_w" if profile.endswith("_w") or (not profile.endswith("_m") and gender == "Weiblich") else "_m"
    return "Fussball_" + band + ("" if band in ("U11", "U13") else suffix)


def storage_profile(profile, sport):
    if sport == "Fussball":
        return profile
    band = profile.split("_")[1]
    return "Leichtathletik_" + band + ("" if band in ("U11", "U13", "U15") else profile[-2:])


def focus_abc_profile(profile, focus):
    return storage_profile(profile, "Leichtathletik") if focus == "speed_jump" else profile


def focus_settings(record, focus):
    saved = record.get("fussball_schwerpunkte", {}).get(focus)
    if saved is not None:
        return deepcopy(saved)
    plan = deepcopy(record.get("planung", {}))
    if focus != legacy_focus(record):
        plan.pop("abc_step", None)
    m_config = deepcopy(record.get("m_training", {}))
    if m_config:
        m_config["sport"] = "Fussball"
    return {"planung": plan, "m_training": m_config}


def focus_unit_key(record, cycle, te, focus):
    if focus is None:
        return json.dumps([cycle, te], ensure_ascii=False)
    key = json.dumps([cycle, te, focus], ensure_ascii=False)
    old_key = json.dumps([cycle, te], ensure_ascii=False)
    sessions = record.get("einheitenprotokoll", {})
    if key not in sessions and old_key in sessions:
        old_focus = sessions[old_key].get("schwerpunkt", legacy_focus(record))
        if old_focus == focus:
            return old_key
    return key


# Frank Müller, 22.09.2026: caps apply to each tempo run, not total volume.
# U11/U13 have no newly authorized tempo pyramid; retain their short/M-sprints.
SPEED_TEMPO_LIMITS = {
    "Männlich": {"U15": (200, 250), "U17": (300, 350), "U20": (400, 400),
                 "U23": (500, 500), "MASTER": (500, 500)},
    "Weiblich": {"U15": (200, 200), "U17": (300, 300), "U20": (400, 400),
                 "U23": (400, 400), "MASTER": (500, 500)},
}


def speed_tempo_bounds(band, gender):
    return SPEED_TEMPO_LIMITS[gender].get(band, (0, 0))


def speed_jump_defaults(band, gender="Männlich"):
    # Acceleration defaults are editable proposals; recovery rationale:
    # https://pmc.ncbi.nlm.nih.gov/articles/PMC6872694/ (Haugen et al., 2019).
    # Tempo caps and late-cycle window are Frank's method, not literature norms.
    lower, upper = speed_tempo_bounds(band, gender)
    return {"runs": 5, "short_runs": 3,
            "distance_m": 20 if band in ("U11", "U13", "U15") else 30,
            "rest_min_s": 120, "rest_max_s": 180,
            "tempo_enabled": upper > 0, "tempo_cap_m": lower, "entry_step": False,
            "tempo_peak_units": 3, "tempo_percent": 80,
            "tempo_rest_min_s": 180, "tempo_rest_max_s": 300}


def normalize_speed_jump(saved, band, gender):
    config = {**speed_jump_defaults(band, gender), **saved}
    low, high = speed_tempo_bounds(band, gender)
    config["tempo_cap_m"] = max(low, min(config["tempo_cap_m"], high))
    if not high:
        config["tempo_enabled"] = False
    return config


def validate_speed_jump(config, band=None, gender=None):
    if not isinstance(config, dict):
        raise ValueError("Ungültige Speed-and-Jump-Vorgaben.")
    limits = {"runs": (1, 12), "short_runs": (1, 12), "distance_m": (10, 60),
              "rest_min_s": (60, 900), "rest_max_s": (60, 900),
              "tempo_cap_m": (0, 500), "tempo_peak_units": (2, 3),
              "tempo_percent": (50, 95), "tempo_rest_min_s": (60, 900),
              "tempo_rest_max_s": (60, 900)}
    if set(config) - set(limits) - {"tempo_enabled", "entry_step"}:
        raise ValueError("Unbekannte Speed-and-Jump-Vorgabe.")
    for field, value in config.items():
        if field in ("tempo_enabled", "entry_step"):
            if type(value) is not bool:
                raise ValueError("Ungültige Tempolauf-Freigabe.")
            continue
        low, high = limits[field]
        if type(value) is not int or not low <= value <= high:
            raise ValueError("Ungültige Speed-and-Jump-Vorgabe: " + field)
    for prefix, default_min, default_max in (("", 120, 180), ("tempo_", 180, 300)):
        if config.get(prefix+"rest_min_s", default_min) > config.get(prefix+"rest_max_s", default_max):
            raise ValueError("Der Pausenbereich ist vertauscht.")
    if band is not None and gender is not None:
        low, high = speed_tempo_bounds(band, gender)
        cap = config.get("tempo_cap_m", low)
        if not low <= cap <= high:
            raise ValueError(f"Speed and Jump {band}: Tempolauf-Obergrenze muss im Bereich {low}–{high} m liegen.")
        if not high and config.get("tempo_enabled", False):
            raise ValueError("Für U11/U13 ist keine zusätzliche Tempolauf-Pyramide hinterlegt.")


def speed_build_index(te, frequency, role):
    """Count full focus sessions; the short second weekly day does not advance them."""
    return sum(not unit_context(i, frequency, 1, role)[2] for i in range(1, te+1))


def speed_block_one(config, build_index, band=None, gender="Männlich"):
    # Frank's latest sequence. The additional 300-m entry step is optional,
    # not silently enabled from the assistant's suggestion.
    steps = [(2, [50, 50]), (3, [50, 50, 50]), (3, [75, 50, 50]),
             (3, [75, 75, 50]), (3, [75, 75, 75]), (3, [100, 75, 75]),
             (3, [100, 100, 75]), (3, [100, 100, 100])]
    if config.get("entry_step", False):
        steps.insert(1, (2, [50, 50, 50]))
    if build_index < 1:
        return 0, []
    rounds, distances = steps[min(build_index, len(steps))-1]
    cap = 50 if gender == "Weiblich" and band == "U15" else 75 if band == "U15" or (gender == "Weiblich" and band == "U17") else 100
    return rounds, [min(d, cap) for d in distances]


def speed_tempo_distances(config, band, gender, te, total_units, short_day=False,
                          frequency=1, role="Automatisch nach Wochenrhythmus"):
    """Return all six block-2 runs, in order: one pair after each station round.

    Continue 100/100, 150/150, 200/150, 200/200, 250/200, ... . Hold the
    previous pair when a further increase would reach the class cap before
    the last 2–3 units. A cap is a ceiling, not a target forced by a short cycle.
    """
    validate_speed_jump(config, band, gender)
    cfg = {**speed_jump_defaults(band, gender), **config}
    if (not cfg["tempo_enabled"] or short_day or not 1 <= te <= total_units
            or unit_context(te, frequency, 1, role)[2]):
        return []
    cap = cfg["tempo_cap_m"]
    peak_start = total_units - cfg["tempo_peak_units"] + 1
    pair, full_units = [], 0
    for current in range(1, te+1):
        if unit_context(current, frequency, 1, role)[2]:
            continue
        full_units += 1
        if full_units == 1:
            candidate = [100, 100]
        elif full_units == 2:
            candidate = [150, 150]
        elif pair[0] == pair[1]:
            candidate = [min(cap, pair[0]+50), pair[1]]
        else:
            candidate = [pair[0], pair[0]]
        if max(candidate) < cap or current >= peak_start:
            pair = candidate
    return pair * 3


def speed_jump_ui(saved, band, gender, total_units, frequency, role, key, disabled):
    config = normalize_speed_jump(saved, band, gender)
    with st.expander("Speed and Jump: Laufblöcke und Streckenaufbau", expanded=True):
        low, high = speed_tempo_bounds(band, gender)
        if high:
            st.markdown("**Zwei Blöcke: Stationsdurchgang → Läufe → nächster Durchgang**")
            st.caption("Block 1: Einstieg mit zwei Durchgängen à 50 + 50 m, danach drei Durchgänge. Laufreihe: 50/50/50 → 75/50/50 → 75/75/50 → 75/75/75 → 100/75/75 → 100/100/75 → 100/100/100 m. Nach jedem Lauf gleich lange Gehstrecke. Ziel: fußballspezifische Sprintschnelligkeitsausdauer.")
            st.caption(f"Für {band} · {gender}: Block 1 höchstens {max(speed_block_one(config, 8, band, gender)[1])} m je Lauf. Die Beispielreihe wird an dieser Grenze gekappt.")
            config["entry_step"] = st.checkbox("Zusätzliche Einstiegsstufe: zweimal 50 + 50 + 50 m", config["entry_step"], key=key+"entry_step", disabled=disabled)
            st.caption("Optionaler Zwischenschritt: 200 → 300 → 450 Laufmeter in Block 1. Ohne Auswahl gilt die diktierte Folge 200 → 450 → 525 m. Block 2 wird dadurch nicht verändert.")
            st.markdown("**Block 2: zwei längere Läufe nach jedem der drei Stationsdurchgänge**")
            config["tempo_enabled"] = st.checkbox("Tempolauf-Aufbau im Speed-and-Jump-Plan verwenden", config["tempo_enabled"], key=key+"tempo_enabled", disabled=disabled)
            if low != high:
                config["tempo_cap_m"] = st.number_input("Längster Tempolauf am Zyklusende (m)", low, high, int(config["tempo_cap_m"]), step=25,
                    key=key+"tempo_cap_"+band+gender, disabled=disabled)
                st.caption(f"{band} · {gender}: Obergrenze {low}–{high} m nach Leistungsvermögen; Ausgangswert {low} m.")
            else:
                config["tempo_cap_m"] = high
                st.caption(f"{band} · {gender}: höchstens {high} m je längerem Lauf.")
            config["tempo_peak_units"] = st.selectbox("Längste Strecken erst in den letzten … Einheiten", [2, 3], index=config["tempo_peak_units"]-2, key=key+"tempo_peak", disabled=disabled)
            config["tempo_percent"] = st.number_input("Tempolauf-Zieltempo (% der jeweiligen Streckenreferenz)", 50, 95, config["tempo_percent"], key=key+"tempo_percent", disabled=disabled)
            st.caption("Block 2: 100/100 → 150/150 → 200/150 → 200/200 → 250/200 → 250/250 m usw. Jeweils dreimal das Laufpaar, insgesamt sechs Läufe. Nach jedem längeren Lauf 100 m Gehpause. Lohnende Pause durch Partnerwechsel.")
            st.caption("Die Obergrenze erscheint frühestens in den letzten zwei bis drei Einheiten des Makrozyklus. Davor bleibt die vorherige Stufe erhalten. Ein kurzer Zyklus muss die Obergrenze nicht erreichen. Die kürzere zweite Wocheneinheit enthält diese Laufblöcke nicht und zählt nicht als nächste Aufbaustufe.")
            preview = []
            for te in range(1, total_units+1):
                short = unit_context(te, frequency, 1, role)[2]
                n, distances = (0, []) if short else speed_block_one(config, speed_build_index(te, frequency, role), band, gender)
                longer = speed_tempo_distances(config, band, gender, te, total_units, short, frequency, role)
                preview.append({"TE": te, "Block 1: je Durchgang (m)": " / ".join(map(str, distances)) if distances else "kurze zweite Einheit",
                    "Block 1: Durchgänge": n, "Block 1: gesamt (m)": n*sum(distances),
                    "Block 2: je Durchgang (m)": " / ".join(map(str, longer[:2])) if longer else "kein längerer Laufblock",
                    "Block 2: Durchgänge": 3 if longer else 0, "Block 2: gesamt (m)": sum(longer)})
            st.dataframe(pd.DataFrame(preview), hide_index=True)
        st.markdown("**Kurze Beschleunigungen: zweite Wocheneinheit / U11 und U13**")
        st.caption("Diese Vorgaben gelten für die kürzere zweite Einheit sowie U11/U13. Die volle Einheit ab U15 verwendet die oben beschriebenen Laufblöcke.")
        cols = st.columns(3)
        config["runs"] = cols[0].number_input("Beschleunigungen: Anzahl", 1, 12, int(config["runs"]), key=key+"runs", disabled=disabled)
        config["short_runs"] = cols[1].number_input("Kürzere zweite Einheit: Anzahl", 1, 12, int(config["short_runs"]), key=key+"short", disabled=disabled)
        config["distance_m"] = cols[2].number_input("Beschleunigungen: Strecke (m)", 10, 60, int(config["distance_m"]), key=key+"distance", disabled=disabled)
        st.caption(PARTNER_PAUSE + ". " + PARTNER_ORGANIZATION)
        st.caption("Freigegebene M-Sprints ersetzen an ihrer Einheit die geraden Läufe des ersten Blocks. Keine zusätzliche Verdoppelung des Laufumfangs. Die Tempotabelle bis 800 m bleibt eine Referenztabelle und erweitert die Laufgrenzen nicht.")
    return config


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
    best = {key: (test.get("protokollwerte", {}).get(key) or 0) if "protokollwerte" in test else max(test[key], default=0) for key in JUMP_TESTS}
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
        if "protokollwerte" in test:
            values = test["protokollwerte"]
            if (not isinstance(values, dict) or set(values) != set(JUMP_TESTS)
                    or not any(v is not None for v in values.values())
                    or any(v is not None and (type(v) not in (int, float) or not math.isfinite(v) or not 0 < v <= 100) for v in values.values())):
                raise ValueError("Ungültige Sprung-Protokollwerte.")
            continue
        for key in JUMP_TESTS:
            values = test.get(key)
            if not isinstance(values, list) or len(values) != 3 or any(
                type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100 for v in values):
                raise ValueError("Je Sprungtest sind drei Weiten zwischen 0 und 100 Metern erforderlich; 0 bedeutet nicht gewertet.")
        if not any(v > 0 for key in JUMP_TESTS for v in test[key]):
            raise ValueError("Mindestens eine gültige Sprungweite eintragen.")

# Test capture is separate from profile editing. Empty measurements stay absent.
FIELD_METRICS = {
    "sprint60": "60 m (s)", "shuttle": "Shuttlezeit (s)", "sprint": "Sprintzeit (s)",
    "hop_links": "5er-Hop links (m)", "hop_rechts": "5er-Hop rechts (m)",
    "schluss": "5er-Schlusssprung (m)",
}
FIELD_SHUTTLE_MODES = ["Gemessen", "Gerundeter Gruppenwert", "Nicht angegeben"]
FIELD_COLUMNS = ["Name auf Bogen", "Zuordnung", "Sprintstrecke (m)", *FIELD_METRICS.values(), "Shuttle-Angabe", "Notiz"]
FIELD_MAX_ROWS = 1000
SHUTTLE_FORMS = {"Einfach": 1, "Zweifach": 2, "Dreifach": 3}


def shuttle_definition(form, distance, extra=0):
    if form not in SHUTTLE_FORMS:
        raise ValueError('Bitte Shuttle-Test einfach, zweifach oder dreifach auswählen.')
    way = field_number(distance, 'Strecke je Weg')
    if way is None:
        raise ValueError('Für Shuttle bitte die Strecke je Hin- oder Rückweg eintragen.')
    extra = roster_number(extra, 'Wendezuschlag gesamt (m)', 0, 1000) or 0
    return {'form': form, 'weg_m': way, **({'wendezuschlag_m': extra} if extra else {})}


def shuttle_description(config):
    if not config:
        return 'Shuttle-Anordnung noch offen'
    phases = 2 * SHUTTLE_FORMS[config['form']]
    extra = config.get('wendezuschlag_m', 0)
    turn = f" + {extra:g} m Wendezuschlag" if extra else ""
    return f"{config['form']}: {phases} × {config['weg_m']:g} m{turn} = {phases * config['weg_m'] + extra:g} m gesamt; {phases} Beschleunigungsphasen"


def shuttle_inputs(prefix, saved=None):
    saved = saved or {}
    a, b, c = st.columns(3)
    options = ['Bitte wählen'] + list(SHUTTLE_FORMS)
    form = a.selectbox('Shuttle-Test', options, index=options.index(saved.get('form', 'Bitte wählen')), key=prefix+'_form')
    way = b.text_input('Strecke je Hin- oder Rückweg (m)', value=str(saved.get('weg_m','')), key=prefix+'_way')
    extra = c.text_input('Wendezuschlag gesamt (m; leer = 0)', value=str(saved.get('wendezuschlag_m', '')), key=prefix+'_extra')
    st.caption('Einfach = hin und zurück (2 Wege); zweifach = 4 Wege; dreifach = 6 Wege. Die eingegebene Strecke gilt für einen Weg.')
    try:
        result = shuttle_definition(form, way, extra)
        st.info(shuttle_description(result))
        return result
    except ValueError as exc:
        if form != 'Bitte wählen' and way:
            st.warning(str(exc))
        return None


def field_text(value):
    if value is None or (not isinstance(value, (str, list, dict)) and pd.isna(value)):
        return ""
    return str(value).strip()


def field_number(value, label):
    raw = field_text(value)
    if not raw:
        return None
    if type(value) is bool or not re.fullmatch(r"\d+(?:[.,]\d{1,4})?", raw):
        raise ValueError(f"{label}: Bitte eine Zahl mit Komma oder Punkt eingeben; fehlende Werte leer lassen.")
    number = float(raw.replace(",", "."))
    upper = 10000 if label in ('Strecke je Weg', 'Sprintstrecke (m)') else 1800 if label in (FIELD_METRICS['sprint60'], FIELD_METRICS['shuttle'], FIELD_METRICS['sprint']) else 100
    if not math.isfinite(number) or not 0 < number <= upper:
        raise ValueError(f"{label}: Der Wert muss größer als 0 und höchstens {upper} sein. 0 bitte durch ein leeres Feld ersetzen.")
    return number


def field_identity_map(kader):
    # A sport-qualified label also distinguishes equal names in legacy sections.
    return {f"{name} [{sport}]": (sport, name) for sport, name in roster_options(kader)}


def field_name_key(name):
    return " ".join(unicodedata.normalize("NFC", name).casefold().split())


def field_match(name, sport, identities):
    candidates = [label for label, (s, n) in identities.items()
                  if field_name_key(n) == field_name_key(name) and (not sport or s == sport)]
    return candidates[0] if len(candidates) == 1 else ""


def field_empty_row(name="", identity=""):
    return {"Name auf Bogen": name, "Zuordnung": identity, "Sprintstrecke (m)": "",
            **{label: "" for label in FIELD_METRICS.values()},
            "Shuttle-Angabe": "Nicht angegeben", "Notiz": ""}


def field_display_frame(rows):
    frame = pd.DataFrame(rows)
    for label in FIELD_METRICS.values():
        if label in frame:
            frame[label] = frame[label].map(lambda v: '' if pd.isna(v) else str(v).replace('.',','))
    return frame


def field_sync_grid(key):
    # Commit cell deltas to a separate draft before any view/column change.
    # The widget's own diff is not the authoritative store for hidden columns.
    draft = deepcopy(st.session_state.get('field_draft', []))
    delta = st.session_state.get(key, {}).get('edited_rows', {})
    for index, changes in delta.items():
        index = int(index)
        if 0 <= index < len(draft):
            for label, value in changes.items():
                if label in FIELD_COLUMNS and label != 'Name auf Bogen':
                    draft[index][label] = field_text(value)
    st.session_state.field_draft = draft
    st.session_state.field_current_rows = deepcopy(draft)


def field_date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(field_text(value), fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Testdatum als TT.MM.JJJJ oder JJJJ-MM-TT angeben.")


def field_csv(rows, datum, bogen, identities, shuttle=None, default_mode='Nicht angegeben'):
    stream = io.StringIO(newline="")
    labels = ["Name", "Kaderbereich", "Datum", "Testbezeichnung", *FIELD_METRICS.values(), "Shuttle-Angabe", "Notiz", "Shuttleform", "Strecke je Weg (m)", "Wendezuschlag gesamt (m)", "Sprintstrecke (m)"]
    writer = csv.DictWriter(stream, labels, delimiter=";", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        sport, name = identities.get(row.get("Zuordnung"), ("", row.get("Name auf Bogen", "")))
        record = {"Name": name, "Kaderbereich": sport, "Datum": datum, "Testbezeichnung": bogen,
                  **{k: field_text(row.get(k)) for k in labels[4:]},
                  'Shuttleform': (shuttle or {}).get('form',''), 'Strecke je Weg (m)': (shuttle or {}).get('weg_m',''), 'Wendezuschlag gesamt (m)': (shuttle or {}).get('wendezuschlag_m','')}
        if record.get('Shuttle-Angabe') in ('','Nicht angegeben'):
            record['Shuttle-Angabe'] = default_mode
        # Prevent spreadsheet formula evaluation when a note/name starts with = etc.
        record = {k: ("'" + str(v) if str(v).lstrip().startswith(("=", "+", "-", "@")) else v) for k, v in record.items()}
        writer.writerow(record)
    return stream.getvalue().encode("utf-8-sig")


def read_field_file(data, filename, identities):
    if len(data) > 10_000_000:
        raise ValueError("Bitte höchstens 10 MB je Tabelle hochladen.")
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("cp1252")
        if text.lower().startswith("sep="):
            text = text.split("\n", 1)[1]
        header = text.splitlines()[0] if text.splitlines() else ""
        separator = ";" if ";" in header else "\t" if "\t" in header else ","
        table = list(csv.reader(io.StringIO(text), delimiter=separator))
    elif suffix == ".xlsx":
        from openpyxl import load_workbook
        try:
            with ZipFile(io.BytesIO(data)) as archive:
                if sum(i.file_size for i in archive.infolist()) > 50_000_000:
                    raise ValueError("Die entpackte Excel-Datei ist zu groß.")
            book = load_workbook(io.BytesIO(data), read_only=True, data_only=False, keep_links=False)
            sheets = [s for s in book.worksheets if s.sheet_state == 'visible']
            if len(sheets) != 1:
                book.close()
                raise ValueError("Bitte eine Excel-Datei mit genau einem sichtbaren Tabellenblatt verwenden.")
            sheet = sheets[0]
            if (sheet.max_column or 0) > 40 or (sheet.max_row or 0) > FIELD_MAX_ROWS + 1:
                book.close()
                raise ValueError("Excel-Tabelle: höchstens 1000 Personen und 40 Spalten.")
            table = list(sheet.iter_rows(max_row=min(sheet.max_row or FIELD_MAX_ROWS+2, FIELD_MAX_ROWS+2),
                                         max_col=min(sheet.max_column or 41,41),values_only=True))
            book.close()
        except (BadZipFile, KeyError, OSError) as exc:
            raise ValueError("Die Excel-Datei konnte nicht gelesen werden.") from exc
    else:
        raise ValueError("Zum direkten Import bitte CSV oder XLSX verwenden. PDF und Fotos können als Vorlage angezeigt werden.")
    if not table or len(table) > FIELD_MAX_ROWS + 1:
        raise ValueError("Die Tabelle ist leer oder enthält mehr als 1000 Personen.")
    headers = [field_text(v) for v in table[0]]
    # Ignore genuinely empty trailing columns, never populated unknown columns.
    while headers and not headers[-1] and all(len(r) < len(headers) or not field_text(r[len(headers)-1]) for r in table[1:]):
        headers.pop()
    allowed = {"Name", "Kaderbereich", "Datum", "Testbezeichnung", *FIELD_METRICS.values(), "Shuttle-Angabe", "Notiz", "Shuttleform", "Strecke je Weg (m)", "Wendezuschlag gesamt (m)", "Sprintstrecke (m)"}
    if len(set(headers)) != len(headers) or "Name" not in headers or set(headers) - allowed:
        raise ValueError("Spaltenüberschriften passen nicht. Bitte die CSV-Vorlage verwenden; sie lässt sich auch in Excel öffnen. Erlaubt: " + ", ".join(sorted(allowed)))
    if not set(FIELD_METRICS.values()) & set(headers):
        raise ValueError("Keine Testwert-Spalte gefunden.")
    rows, dates, titles, shuttles = [], set(), set(), set()
    for index, values in enumerate(table[1:], 2):
        if not any(field_text(v) for v in values):
            continue
        if len(values) > len(headers) and any(field_text(v) for v in values[len(headers):]):
            raise ValueError(f"Zeile {index}: zusätzliche Werte ohne Spaltenüberschrift.")
        record = dict(zip(headers, values))
        for k, v in list(record.items()):
            if isinstance(v, str) and v.startswith("'") and v[1:].lstrip().startswith(("=", "+", "-", "@")):
                record[k] = v[1:]
        name = field_text(record.get("Name"))
        if not name or len(name) > 120:
            raise ValueError(f"Zeile {index}: Namen bis 120 Zeichen eintragen.")
        row = field_empty_row(name, field_match(name, field_text(record.get("Kaderbereich")), identities))
        for label in FIELD_METRICS.values():
            # Preserve suspect input for manual correction in the table.
            row[label] = field_text(record.get(label))
        row["Shuttle-Angabe"] = field_text(record.get("Shuttle-Angabe")) or "Nicht angegeben"
        row["Notiz"] = field_text(record.get("Notiz"))
        row["Sprintstrecke (m)"] = field_text(record.get("Sprintstrecke (m)"))
        if field_text(record.get("Datum")):
            dates.add(field_date(record['Datum']))
        if field_text(record.get("Testbezeichnung")):
            titles.add(field_text(record['Testbezeichnung']))
        if field_text(record.get('Shuttleform')) or field_text(record.get('Strecke je Weg (m)'), record.get('Wendezuschlag gesamt (m)')):
            config = shuttle_definition(field_text(record.get('Shuttleform')), record.get('Strecke je Weg (m)'), record.get('Wendezuschlag gesamt (m)'))
            shuttles.add((config['form'],config['weg_m'],config.get('wendezuschlag_m',0)))
        rows.append(row)
    if len(dates) > 1 or len(titles) > 1 or len(shuttles) > 1:
        raise ValueError("Bitte pro Import ein Testdatum, eine Testbezeichnung und eine Shuttle-Anordnung verwenden.")
    if not rows:
        raise ValueError("Die Datei enthält keine Personen.")
    shuttle = shuttle_definition(*next(iter(shuttles))) if shuttles else None
    return rows, next(iter(dates), None), next(iter(titles), None), shuttle


def validate_field_tests(tests):
    if not isinstance(tests, list) or len(tests) > 10000:
        raise ValueError("Ungültiger Feldtest-Verlauf.")
    ids = set()
    for event in tests:
        if not isinstance(event, dict):
            raise ValueError("Ungültiger Feldtest.")
        field_date(event.get('datum'))
        if not isinstance(event.get('id'), str) or event['id'] in ids:
            raise ValueError("Doppelter oder ungültiger Feldtest.")
        ids.add(event['id'])
        if not isinstance(event.get('bogen'), str) or not 0 < len(event['bogen']) <= 120:
            raise ValueError("Testbezeichnung prüfen.")
        values = event.get('werte')
        if not isinstance(values, dict) or set(values) - set(FIELD_METRICS) or not values:
            raise ValueError("Ungültige Testwerte.")
        for k, v in values.items():
            if field_number(v, FIELD_METRICS[k]) is None:
                raise ValueError("Fehlende Werte dürfen nicht als Messergebnis gespeichert werden.")
        if 'sprint' in values and field_number(event.get('sprint_m'), 'Sprintstrecke (m)') is None:
            raise ValueError('Sprintstrecke fehlt.')
        if 'shuttle' in values:
            config = event.get('shuttle')
            if not isinstance(config, dict) or shuttle_definition(config.get('form'),config.get('weg_m'),config.get('wendezuschlag_m',0)) != config:
                raise ValueError('Shuttle-Anordnung prüfen.')
        if event.get('shuttle_angabe') not in FIELD_SHUTTLE_MODES:
            raise ValueError("Herkunft der Shuttlezeit prüfen.")
        if not isinstance(event.get('notiz'), str) or len(event['notiz']) > 4000:
            raise ValueError("Testnotiz zu lang.")
        history = event.get('aenderungen', [])
        if not isinstance(history, list) or len(history) > 200:
            raise ValueError("Zu viele Korrekturen dieses Tests.")
        for prior in history:
            if not isinstance(prior, dict) or 'aenderungen' in prior:
                raise ValueError("Ungültiger Korrekturverlauf.")
            validate_field_tests([prior])


def prepare_field_batch(kader, rows, datum, bogen, correct=False, use_reference=False, shuttle=None, default_mode='Gemessen'):
    """Pure preview. Caller commits the entire validated candidate with its revision."""
    datum = field_date(datum)
    bogen = field_text(bogen)
    if not bogen or len(bogen) > 120:
        raise ValueError("Bitte eine Testbezeichnung mit 1 bis 120 Zeichen angeben.")
    if not rows or len(rows) > FIELD_MAX_ROWS:
        raise ValueError("Bitte 1 bis 1000 Personen in der Tabelle erfassen.")
    identities = field_identity_map(kader)
    updated = deepcopy(kader)
    seen, errors, preview = set(), [], []
    changed, skipped = 0, 0
    stamp = datetime.now(timezone.utc).isoformat()
    for index, row in enumerate(rows, 1):
        try:
            values = {k: field_number(row.get(label), label) for k, label in FIELD_METRICS.items()}
            values = {k: v for k, v in values.items() if v is not None}
            if not values:
                skipped += 1
                continue
            identity = field_text(row.get('Zuordnung'))
            if identity not in identities:
                raise ValueError("Bitte eine vorhandene Person in ‚Zuordnung‘ auswählen.")
            if identity in seen:
                raise ValueError("Diese Person ist mehrfach enthalten. Bitte die Zeilen zusammenführen.")
            seen.add(identity)
            sport, name = identities[identity]
            note = field_text(row.get('Notiz'))
            mode = field_text(row.get('Shuttle-Angabe')) or 'Nicht angegeben'
            if mode == 'Nicht angegeben':
                mode = default_mode
            if mode not in FIELD_SHUTTLE_MODES or len(note) > 4000:
                raise ValueError("Shuttle-Angabe oder Notiz prüfen.")
            if 'shuttle' in values:
                if not shuttle:
                    raise ValueError('Für die Shuttlezeit bitte Shuttle-Test und Strecke je Weg festlegen.')
                shuttle = shuttle_definition(shuttle.get('form'),shuttle.get('weg_m'),shuttle.get('wendezuschlag_m',0))
            sprint_m = field_number(row.get('Sprintstrecke (m)'), 'Sprintstrecke (m)') if 'sprint' in values else None
            if 'sprint' in values and sprint_m is None:
                raise ValueError('Sprintstrecke fehlt.')
            rec = updated[sport][name]
            event_id = hashlib.sha256(json.dumps([datum, bogen.casefold()], ensure_ascii=False).encode()).hexdigest()
            events = rec.setdefault('feldtests', [])
            old = next((e for e in events if e['id'] == event_id), None)
            conflicting = [FIELD_METRICS[k] for k, v in values.items() if old and k in old['werte'] and old['werte'][k] != v]
            if old and 'sprint' in old['werte'] and 'sprint' in values and old.get('sprint_m') != sprint_m:
                raise ValueError('Andere Sprintstrecke: bitte eine eigene Testbezeichnung verwenden.')
            if old and 'shuttle' in old['werte'] and 'shuttle' in values and mode != 'Nicht angegeben' and mode != old['shuttle_angabe']:
                conflicting.append('Shuttle-Angabe')
            if old and 'shuttle' in old['werte'] and 'shuttle' in values and old.get('shuttle') != shuttle:
                conflicting.append('Shuttle-Anordnung (für einen anderen Test bitte eine eigene Testbezeichnung verwenden)')
            if old and note and old['notiz'] and note != old['notiz']:
                conflicting.append('Notiz')
            if conflicting and not correct:
                raise ValueError('Bereits gespeichert, abweichend: ' + ', '.join(conflicting) + '. Korrektur ausdrücklich auswählen oder Eingabe berichtigen.')
            event = deepcopy(old) if old else {'id': event_id, 'datum': datum, 'bogen': bogen, 'werte': {}, 'shuttle_angabe': 'Nicht angegeben', 'notiz': '', 'aenderungen': []}
            event['werte'].update(values)
            if 'sprint' in values:
                event['sprint_m'] = sprint_m
            if 'shuttle' in values:
                event['shuttle'] = deepcopy(shuttle)
            if 'shuttle' in values and mode != 'Nicht angegeben':
                event['shuttle_angabe'] = mode
            if note:
                event['notiz'] = note
            change = old is None or any(event.get(k) != old.get(k) for k in ('werte', 'shuttle_angabe', 'notiz', 'shuttle', 'sprint_m'))
            reference_change = False
            if use_reference and 'sprint60' in values:
                if not 6 <= values['sprint60'] <= 15:
                    raise ValueError('60-m-Referenz der bisherigen Planung erlaubt 6 bis 15 s. Als Testwert ist die Zeit ohne Referenzübernahme speicherbar.')
                reference_change = rec.get('t_60') != values['sprint60']
                rec['t_60'] = values['sprint60']
                if rec.get('t_150_quelle') == 'berechnet':
                    rec['t_150'] = round(rec['t_60'] * 2.375, 2)
            if change:
                if old:
                    prior = deepcopy(old)
                    prior.pop('aenderungen', None)
                    event['aenderungen'].append(prior)
                    events[events.index(old)] = event
                else:
                    events.append(event)
                event['gespeichert_am'] = stamp
                jumps = {k: event['werte'].get(k) for k in JUMP_TESTS}
                if any(v is not None for v in jumps.values()):
                    tests = rec.setdefault('sprungtests', [])
                    test = {'datum': datum, 'notizen': ('Protokollwerte; Einzelversuche nicht angegeben. ' + event['notiz']).strip()[:4000],
                            'protokollwerte': jumps, 'feldtest_id': event_id}
                    existing_jump = next((j for j in tests if j.get('feldtest_id') == event_id), None)
                    if existing_jump:
                        tests[tests.index(existing_jump)] = test
                    else:
                        tests.append(test)
            status = ('Korrektur' if conflicting else 'Ergänzung' if old else 'Neu') if change else 'Bereits gespeichert'
            if reference_change:
                status += '; 60-m-Referenz geändert'
            changed += bool(change or reference_change)
            preview.append({'Person': name, 'Status': status,
                            **{label: values.get(k) for k, label in FIELD_METRICS.items()},
                            'Sprintstrecke (m)': event.get('sprint_m',60 if 'sprint60' in event['werte'] else None),
                            'Shuttle-Test':shuttle_description(event.get('shuttle')) if 'shuttle' in event['werte'] else '',
                            'Shuttle-Angabe': event['shuttle_angabe'], 'Notiz': event['notiz']})
        except (ValueError, TypeError) as exc:
            errors.append(f"Zeile {index} ({field_text(row.get('Name auf Bogen'))}): {exc}")
    if errors:
        raise ValueError('\n'.join(errors[:30]))
    if not preview:
        raise ValueError('Noch keine Testwerte eingetragen. Leere Zeilen werden nicht gespeichert.')
    validate_kader(updated)
    return updated, preview, changed, skipped


def field_sheet_pdf(names, datum, title, shuttle=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=14*mm)
    style = ParagraphStyle('field', fontName='Helvetica', fontSize=10, leading=13)
    header = ParagraphStyle('header', parent=style, fontName='Helvetica-Bold', fontSize=17, leading=21)
    names = names or ['']*6
    story = []
    for start in range(0, len(names), 6):
        if start:
            story.append(PageBreak())
        chunk = names[start:start+6]
        story += [Paragraph('Doc Athletic - Testprotokoll', header), Spacer(1, 3*mm),
                  Paragraph(escape(title) + ' | Datum: ' + escape(datum), style),
                  Spacer(1, 3*mm), Paragraph('Groß und eindeutig schreiben. Fehlende Werte leer lassen. Korrekturen daneben neu eintragen.', style),
                  Paragraph(escape(shuttle_description(shuttle)),style), Spacer(1, 5*mm)]
        for section, labels, widths in [
            ('Laufzeiten', ['Name', '60 m (s)', 'Shuttlezeit (s)'], [80*mm, 45*mm, 55*mm]),
            ('Sprungweiten: jeweils fünf Sprünge, Gesamtweite in Metern', ['Name', '5er-Hop links\n(m)', '5er-Hop rechts\n(m)', '5er-Schluss\n(m)'], [66*mm, 38*mm, 38*mm, 38*mm])]:
            story += [Paragraph(section, style), Spacer(1, 2*mm)]
            content = [[Paragraph(escape(x).replace('\n','<br/>'), style) for x in labels]]
            content += [[Paragraph(escape(n), style)] + ['']*(len(labels)-1) for n in chunk]
            table = Table(content, colWidths=widths, rowHeights=[14*mm]+[13*mm]*len(chunk))
            table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1.3,colors.black), ('BOX',(0,0),(-1,-1),1.8,colors.black),
                                      ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef2')),
                                      ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('LEFTPADDING',(0,0),(-1,-1),7)]))
            story += [table, Spacer(1, 5*mm)]
        story += [Paragraph('Shuttle-Angabe: gemessen / gerundeter Gruppenwert (bitte kennzeichnen).<br/>Sprungwerte: Protokoll-/Bestwert. Einzelversuche sind auf diesem Bogen nicht getrennt erfasst.<br/>Bedingungen / Notizen: __________________________________________________', style)]
    doc.build(story)
    return out.getvalue()


def render_field_history(record):
    events = record.get('feldtests', [])
    if not events:
        return
    with st.expander('Feldtests aus Testtabelle / Dateiimport'):
        rows = [{'Datum': e['datum'], 'Test': e['bogen'], **{label:e['werte'].get(k) for k,label in FIELD_METRICS.items()},
                 'Sprintstrecke (m)': e.get('sprint_m',60 if 'sprint60' in e['werte'] else None),
                 'Shuttle-Test':shuttle_description(e.get('shuttle')) if 'shuttle' in e['werte'] else '',
                 'Shuttle-Angabe':e['shuttle_angabe'], 'Notiz':e['notiz']} for e in events]
        st.dataframe(field_display_frame(rows), hide_index=True, width='stretch')
        st.caption('Shuttle bleibt von geraden Laufstrecken getrennt. Sprung-Protokollwerte erscheinen auch im Sprungtest-Verlauf. Fehlende Einzelversuche werden nicht erfunden.')
        if any(e.get('aenderungen') for e in events):
            with st.expander('Frühere Werte nach Korrekturen'):
                for e in events:
                    for old in e.get('aenderungen', []):
                        st.write({'Datum':old['datum'], 'Test':old['bogen'], 'Werte':old['werte'], 'Notiz':old['notiz']})


def render_field_reference():
    with st.expander('PDF / Foto daneben ansehen (ohne automatische Erkennung)'):
        upload = st.file_uploader('Bogen oder Screenshot als Vorlage', type=['pdf','jpg','jpeg','png'], key='field_reference')
        st.caption('Diese Datei wird nur zur Ansicht geladen. Werte bitte in die Tabelle übertragen; digital ausgefüllte CSV-/Excel-Tabellen lassen sich direkt importieren.')
        if upload is None:
            return
        if upload.size > 10_000_000:
            st.error('Vorlage höchstens 10 MB. Größere Scans bitte aufteilen.')
            return
        data = upload.getvalue()
        try:
            if upload.name.lower().endswith('.pdf'):
                import pypdfium2 as pdfium
                document = pdfium.PdfDocument(data)
                try:
                    if not 1 <= len(document) <= 20:
                        raise ValueError('Bitte einen Scan mit 1 bis 20 Seiten hochladen.')
                    page_index = st.number_input('Seite der Vorlage', 1, len(document), 1, key='field_ref_page')-1
                    page = document[page_index]
                    try:
                        scale = min(2., 1600/max(page.get_width(), page.get_height()))
                        bitmap = page.render(scale=scale)
                        try:
                            picture = bitmap.to_pil()
                            st.image(picture, width='stretch')
                        finally:
                            bitmap.close()
                    finally:
                        page.close()
                finally:
                    document.close()
            else:
                st.image(data, width='stretch')
        except ImportError:
            st.error('Für die PDF-Ansicht bitte auch die neue requirements.txt übernehmen.')
        except Exception:
            st.error('Diese Vorlage konnte nicht angezeigt werden. Bitte PDF, JPG oder PNG prüfen.')


def render_individual_shuttle(record, sport, name, profile_for_save, guest):
    if name not in st.session_state.kader_db.get(sport, {}):
        return
    with st.expander('Shuttle-Test: einfach, zweifach, dreifach'):
        if guest:
            st.caption('Neue Testergebnisse können Trainer erfassen.')
            return
        key = 'single_shuttle_' + hashlib.sha256((sport+name).encode()).hexdigest()[:12]
        config = shuttle_inputs(key)
        d = st.date_input('Datum des Shuttle-Tests', key=key+'_date')
        title = st.text_input('Shuttle-Testbezeichnung', value='Shuttle-Test', key=key+'_title')
        seconds = st.text_input('Shuttle-Zeit (s)', key=key+'_seconds')
        mode = st.selectbox('Shuttle-Zeitangabe', FIELD_SHUTTLE_MODES, key=key+'_mode')
        note = st.text_input('Shuttle-Notiz', key=key+'_note')
        correct = st.checkbox('Gespeicherten Shuttle-Test dieses Datums korrigieren', key=key+'_correct')
        st.caption('Speichert auch die aktuell bearbeiteten Profilwerte. Bei einem anderen Test am selben Datum eine andere Testbezeichnung verwenden.')
        if st.button('Shuttle-Test speichern', key=key+'_save'):
            try:
                if field_number(seconds, FIELD_METRICS['shuttle']) is None:
                    raise ValueError('Bitte eine Shuttle-Zeit eingeben.')
                current = deepcopy(st.session_state.kader_db)
                current[sport][name] = profile_for_save()
                identity = f'{name} [{sport}]'
                row = field_empty_row(name, identity)
                row.update({FIELD_METRICS['shuttle']:seconds, 'Shuttle-Angabe':mode,'Notiz':note})
                candidate, _, changed, _ = prepare_field_batch(current,[row],d.isoformat(),title,correct=correct,shuttle=config)
                if not changed and candidate == st.session_state.kader_db:
                    st.info('Dieser Test ist bereits gespeichert.')
                else:
                    revision = speichere_kader_in_datei(candidate,st.session_state.kader_revision)
                    st.session_state.kader_db = candidate
                    st.session_state.kader_revision = revision
                    st.session_state.edit_epoch = st.session_state.get('edit_epoch',0)+1
                    st.session_state.save_notice = f'Shuttle-Test und Profilwerte für {name} gespeichert.'
                    st.rerun()
            except (ValueError, OSError, sqlite3.Error, StorageError, StorageConflict) as exc:
                st.error(f'Nicht gespeichert: {exc}')


def render_test_table():
    st.title('Testtabelle und Dateiimport')
    capture_mode = st.radio('Erfassungsart', ['Kader und Tests aus Tabelle', 'Testwerte vorhandener Personen'], key='capture_mode', persist_state='session')
    if capture_mode == 'Kader und Tests aus Tabelle':
        render_roster_import()
        return
    st.button('Zur Trainingsplanung', on_click=navigiere, args=('Operativ',))
    st.caption('Am Tablet direkt eintragen oder eine ausgefüllte CSV-/Excel-Tabelle laden. Ein Testdatum je Tabelle; bis zu 1000 Personen. Pro Sprungdisziplin ein Protokoll-/Bestwert.')
    identities = field_identity_map(st.session_state.kader_db)
    if not identities:
        st.info('Zuerst die Personen im Kader anlegen. Danach können ihre Testwerte gemeinsam erfasst werden.')
    draft = st.session_state.get('field_draft')
    with st.expander('Neue Tabelle / Datei laden', expanded=draft is None):
        names = st.multiselect('Personen aus dem Kader', list(identities), default=list(identities), key='field_roster_select')
        allow_replace = st.checkbox('Vorhandenen Tabellenentwurf ersetzen', key='field_replace') if draft is not None else True
        if len(names) > FIELD_MAX_ROWS:
            st.info('Bitte höchstens 1000 Personen je Testtabelle auswählen.')
        if st.button('Leere Testtabelle öffnen', disabled=not names or len(names)>FIELD_MAX_ROWS or not allow_replace):
            st.session_state.field_draft = [field_empty_row(identities[n][1], n) for n in names]
            st.session_state.field_epoch = st.session_state.get('field_epoch',0)+1
            st.session_state.pop('field_preview', None)
            st.rerun()
        upload = st.file_uploader('Ausgefüllte Tabelle (CSV oder Excel)', type=['csv','xlsx'], key='field_import_file')
        st.caption('Spaltennamen aus der Vorlage beibehalten. Excel: ein sichtbares Tabellenblatt, keine Formeln in Messwerten. Namen werden nur bei eindeutiger Übereinstimmung zugeordnet.')
        if st.button('Datei in die Kontrolltabelle laden', disabled=upload is None or not allow_replace):
            try:
                rows, datum, title, shuttle = read_field_file(upload.getvalue(), upload.name, identities)
                st.session_state.field_draft = rows
                st.session_state.field_epoch = st.session_state.get('field_epoch',0)+1
                st.session_state.field_pending_metadata = (datum, title, shuttle)
                st.session_state.pop('field_preview', None)
                st.rerun()
            except ImportError:
                st.error('Für Excel bitte die neue requirements.txt übernehmen. CSV funktioniert ohne die zusätzliche Excel-Bibliothek.')
            except Exception as exc:
                st.error(f'Datei nicht geladen: {exc}')
    pending = st.session_state.pop('field_pending_metadata', None)
    if pending:
        st.session_state['field_date'] = date.fromisoformat(pending[0]) if pending[0] else date.today()
        st.session_state['field_title'] = pending[1] or 'Leistungsanalyse'
        st.session_state['field_shuttle_form'] = (pending[2] or {}).get('form','Bitte wählen')
        st.session_state['field_shuttle_way'] = str((pending[2] or {}).get('weg_m',''))
        st.session_state['field_shuttle_extra'] = str((pending[2] or {}).get('wendezuschlag_m',''))
        if not pending[0]:
            st.warning('Die Datei enthält kein Testdatum. Bitte das Datum unten einstellen.')
    retained = st.session_state.get('field_metadata', {})
    for k, v in retained.items():
        if k not in st.session_state:
            st.session_state[k] = v
    left, right = st.columns([1,2])
    datum = left.date_input('Gemeinsames Testdatum', key='field_date')
    title = right.text_input('Testbezeichnung', value='Leistungsanalyse', max_chars=120, key='field_title')
    shuttle = shuttle_inputs('field_shuttle')
    default_mode = st.selectbox('Shuttle-Angabe für Zeilen ohne eigene Angabe', FIELD_SHUTTLE_MODES, key='field_default_mode')
    st.session_state.field_metadata = {k:st.session_state[k] for k in ('field_date','field_title','field_shuttle_form','field_shuttle_way','field_shuttle_extra','field_default_mode')}
    template_rows = [field_empty_row(identities[n][1], n) for n in names] or [field_empty_row('Name eintragen')]
    c1, c2 = st.columns(2)
    c1.download_button('CSV-Vorlage herunterladen', field_csv(template_rows, datum.isoformat(), title, identities, shuttle, default_mode),
                       file_name='Doc_Athletic_Testvorlage.csv', mime='text/csv')
    paper_key = json.dumps([names,datum.isoformat(),title,shuttle],ensure_ascii=False)
    if c2.button('Papierbogen vorbereiten (PDF)'):
        try:
            content = field_sheet_pdf([identities[n][1] for n in names], datum.strftime('%d.%m.%Y'), title, shuttle)
            st.session_state.field_paper = content
            st.session_state.field_paper_key = paper_key
        except ImportError:
            st.error('Für den Papierbogen bitte die neue requirements.txt übernehmen.')
    if 'field_paper' in st.session_state and st.session_state.get('field_paper_key')==paper_key:
        st.download_button('Papierbogen herunterladen', st.session_state.field_paper, file_name='Doc_Athletic_Testbogen.pdf', mime='application/pdf')
    draft = st.session_state.get('field_draft')
    if draft is None:
        return
    if any(not r.get('Zuordnung') for r in draft):
        st.info('Nicht eindeutig erkannte Namen: bitte in der Spalte ‚Zuordnung‘ die richtige Person auswählen. Es werden keine neuen Profile automatisch angelegt.')
    st.markdown('**Werte eintragen und kontrollieren**')
    st.caption('Komma oder Punkt möglich. Leeres Feld = kein Ergebnis. 0 wird nicht als Messergebnis übernommen. Für gerundete Shuttlezeiten ‚Gerundeter Gruppenwert‘ wählen; es wird nicht automatisch gerundet.')
    block = st.radio('Angezeigte Testspalten', ['Laufzeiten','Sprungweiten','Alle Werte'], horizontal=True, key='field_view')
    st.caption('Der Wechsel zwischen Laufzeiten und Sprungweiten erhält die Eingaben. Für mehr Platz das Vollbildsymbol rechts oben in der Tabelle verwenden.')
    if st.checkbox('Scan / Foto neben der Tabelle anzeigen', key='field_show_reference'):
        table_column, reference_column = st.columns([3,2])
        with reference_column:
            render_field_reference()
    else:
        table_column = st.container()
    epoch = st.session_state.get('field_epoch',0)
    config = {label:st.column_config.TextColumn(label, width=160 if k in JUMP_TESTS else 125) for k,label in FIELD_METRICS.items()}
    config.update({'Name auf Bogen':st.column_config.TextColumn('Name auf Bogen',width='medium'),
                   'Zuordnung':st.column_config.SelectboxColumn('Zuordnung', options=list(identities),width='medium'),
                   'Shuttle-Angabe':st.column_config.SelectboxColumn('Shuttle-Angabe',options=FIELD_SHUTTLE_MODES,width='medium'),
                   'Notiz':st.column_config.TextColumn('Notiz',width='large')})
    source_needed = any(r.get('Name auf Bogen') != identities.get(r.get('Zuordnung'),('', ''))[1] for r in draft)
    order = (['Name auf Bogen'] if source_needed else []) + ['Zuordnung']
    order += [FIELD_METRICS[k] for k in (['sprint60','shuttle'] if block=='Laufzeiten' else list(JUMP_TESTS) if block=='Sprungweiten' else list(FIELD_METRICS))]
    if block != 'Sprungweiten':
        order += ['Sprintstrecke (m)', FIELD_METRICS['sprint']] if FIELD_METRICS['sprint'] not in order else ['Sprintstrecke (m)']
        order += ['Shuttle-Angabe','Notiz']
    with table_column:
        edited = st.data_editor(pd.DataFrame(draft, columns=FIELD_COLUMNS).astype(str), hide_index=True, width='stretch',
                                height=440, row_height=44, column_config=config, column_order=order, disabled=['Name auf Bogen'],
                                key=f'field_grid_{epoch}', num_rows='fixed', on_change=field_sync_grid, args=(f'field_grid_{epoch}',))
    rows = edited.to_dict('records')
    # Separate non-widget state survives navigation without binding edits to another athlete.
    st.session_state.field_current_rows = rows
    st.download_button('Aktuellen Tabellenentwurf sichern (CSV)', field_csv(rows, datum.isoformat(), title, identities, shuttle, default_mode),
                       file_name='Doc_Athletic_Testerfassung.csv', mime='text/csv')
    correct = st.checkbox('Abweichende, bereits gespeicherte Werte korrigieren (alter Stand bleibt im Verlauf)', key='field_correct')
    use_reference = st.checkbox('60-m-Werte auch als aktuelle Referenz für die Trainingsplanung übernehmen', key='field_use_reference')
    state = {'rows':rows,'datum':datum.isoformat(),'bogen':title,'correct':correct,'use_reference':use_reference,'shuttle':shuttle,'default_mode':default_mode}
    fingerprint = hashlib.sha256(json.dumps(state, ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if st.button('Eingaben prüfen', type='primary'):
        try:
            candidate, preview, changed, skipped = prepare_field_batch(st.session_state.kader_db, **state)
            st.session_state.field_preview = {'fingerprint':fingerprint,'revision':st.session_state.kader_revision,
                                              'preview':preview,'changed':changed,'skipped':skipped}
        except ValueError as exc:
            st.session_state.pop('field_preview', None)
            st.error(str(exc))
    checked = st.session_state.get('field_preview')
    if checked and checked['fingerprint'] == fingerprint:
        st.subheader('Kontrolle vor dem Speichern')
        summary = field_display_frame(checked['preview'])
        visible = [k for k in summary if k not in FIELD_METRICS.values() or any(summary[k] != '')]
        st.dataframe(summary[visible], hide_index=True, width='stretch')
        st.caption(f"{checked['changed']} Personen mit Änderungen; {checked['skipped']} leere Zeilen ausgelassen. Datum: {datum.strftime('%d.%m.%Y')}. Test: {title}.")
        if st.button('Geprüfte Testwerte gemeinsam speichern', disabled=not checked['changed'], type='primary'):
            try:
                if checked['revision'] != st.session_state.kader_revision:
                    raise StorageConflict('Der Kader hat sich seit der Prüfung geändert. Bitte erneut prüfen.')
                candidate, preview, changed, skipped = prepare_field_batch(st.session_state.kader_db, **state)
                rev = speichere_kader_in_datei(candidate, checked['revision'])
                st.session_state.kader_db = candidate
                st.session_state.kader_revision = rev
                st.session_state.edit_epoch = st.session_state.get('edit_epoch',0)+1
                st.session_state.save_notice = f'Testwerte für {changed} Personen gemeinsam gespeichert. Profile und Trainingspläne bleiben erhalten.'
                st.session_state.field_draft = rows
                st.session_state.field_epoch = epoch+1
                st.session_state.pop('field_preview',None)
                st.rerun()
            except (OSError, sqlite3.Error, StorageError, StorageConflict, ValueError) as exc:
                st.error(f'Nichts gespeichert: {exc}. Den Tabellenentwurf als CSV sichern; bei einem Sitzungskonflikt den Kader neu laden und erneut prüfen.')
    elif checked:
        st.info('Eingaben wurden geändert. Bitte erneut prüfen.')


# Team-table input is parsed as data only; no workbook formulas or scripts run.
ROSTER_LABELS = ['Name', 'Alter (Jahre)', 'Geschlecht', 'Altersklasse', 'Gewicht (kg)',
    'Körperlänge (cm)', 'Typ', 'Entwicklungsstand', 'TE pro Woche', 'Sprintstrecke (m)',
    'Sprintzeit (s)', 'Shuttle: einfache Strecke (m)', 'Shuttle-Anzahl (1/2/3)',
    'Wendezuschlag gesamt (m)', 'Shuttlezeit (s)', '5er-Hop links (m)',
    '5er-Hop rechts (m)', '5er-Schlusssprung (m)', 'Shuttle-Angabe', 'Notiz']
ROSTER_NEW = 'Neues Profil anlegen'


def roster_number(value, label, low, high, whole=False):
    raw = field_text(value)
    if not raw:
        return None
    if type(value) is bool or not re.fullmatch(r'\d+(?:[.,]\d{1,4})?', raw):
        raise ValueError(f'{label}: Zahl mit Komma oder Punkt eingeben.')
    number = float(raw.replace(',', '.'))
    if not math.isfinite(number) or not low <= number <= high or (whole and number != int(number)):
        raise ValueError(f'{label}: {low} bis {high}' + (' als ganze Zahl.' if whole else '.'))
    return int(number) if whole else number


def roster_header(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', field_text(value)).casefold())


def roster_table(data, filename):
    if len(data) > 10_000_000:
        raise ValueError('Bitte höchstens 10 MB je Tabelle hochladen.')
    suffix = Path(filename).suffix.lower()
    limit = FIELD_MAX_ROWS + 20
    if suffix == '.csv':
        try:
            text = data.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = data.decode('cp1252')
        if text.lower().startswith('sep='):
            text = text.split('\n', 1)[1]
        first = text.splitlines()[0] if text.splitlines() else ''
        sep = ';' if ';' in first else '\t' if '\t' in first else ','
        table = list(csv.reader(io.StringIO(text), delimiter=sep))
    elif suffix in ('.xlsx', '.ods'):
        with ZipFile(io.BytesIO(data)) as archive:
            if sum(x.file_size for x in archive.infolist()) > 50_000_000:
                raise ValueError('Die entpackte Tabelle ist zu groß.')
            if suffix == '.ods':
                xml = archive.read('content.xml')
                if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
                    raise ValueError('Diese XML-Struktur wird nicht unterstützt.')
                ns = {'t':'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                      'o':'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                      'x':'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
                root = ET.fromstring(xml)
                sheets = root.findall('o:body/o:spreadsheet/t:table', ns)
                if len(sheets) != 1:
                    raise ValueError('ODS: bitte genau ein Tabellenblatt verwenden.')
                def q(prefix, key):
                    return '{'+ns[prefix]+'}'+key
                def physical_rows(parent):
                    for child in parent:
                        if child.tag == q('t', 'table-row'):
                            yield child
                        elif child.tag in {q('t', t) for t in ('table-header-rows','table-rows','table-row-group')}:
                            yield from physical_rows(child)
                table = []
                row_position = 0
                for row in physical_rows(sheets[0]):
                    repeat = int(row.get(q('t','number-rows-repeated'), '1'))
                    if repeat < 1:
                        raise ValueError('Ungültige Zeilenwiederholung.')
                    values = []
                    col = 0
                    for cell in row:
                        if cell.tag not in {q('t','table-cell'),q('t','covered-table-cell')}:
                            continue
                        count = int(cell.get(q('t','number-columns-repeated'), '1'))
                        if count < 1:
                            raise ValueError('Ungültige Spaltenwiederholung.')
                        kind = cell.get(q('o','value-type'))
                        value = cell.get(q('o','date-value')) if kind == 'date' else cell.get(q('o','value')) if kind in ('float','percentage','currency') else '\n'.join(''.join(p.itertext()) for p in cell.findall('x:p', ns))
                        formula = cell.get(q('t','formula'))
                        if formula:
                            value = {'formula':formula}
                        if value and col + count > 40:
                            raise ValueError('Bitte höchstens 40 Spalten verwenden.')
                        values += [value] * min(count, max(0, 40-col))
                        col += count
                    if any(v not in ('', None) for v in values):
                        if row_position + repeat > limit:
                            raise ValueError('Zu viele Tabellenzeilen.')
                        table += [[None]*40 for _ in range(row_position-len(table))]
                        table += [list(values) for _ in range(repeat)]
                    row_position += repeat
            else:
                from openpyxl import load_workbook
                book = load_workbook(io.BytesIO(data), read_only=True, data_only=False, keep_links=False)
                try:
                    sheets = [s for s in book.worksheets if s.sheet_state == 'visible']
                    if len(sheets) != 1:
                        raise ValueError('Excel: bitte genau ein sichtbares Tabellenblatt verwenden.')
                    sheet = sheets[0]
                    if (sheet.max_column or 0) > 40 or (sheet.max_row or 0) > limit:
                        raise ValueError('Zu viele Zeilen oder Spalten in der Excel-Datei.')
                    table = [[{'formula':c.value} if c.data_type == 'f' else c.value for c in row]
                             for row in sheet.iter_rows(max_row=sheet.max_row or limit, max_col=sheet.max_column or 40)]
                finally:
                    book.close()
    else:
        raise ValueError('Bitte XLSX, ODS oder CSV hochladen. Ein PDF oder Foto enthält hier keine automatisch lesbare Testtabelle.')
    if len(table) > limit or any(len(row) > 40 for row in table):
        raise ValueError('Bitte höchstens 1000 Personen und 40 Spalten verwenden.')
    return table


def read_roster_file(data, filename, identities):
    table = roster_table(data, filename)
    aliases = {roster_header(label):label for label in ROSTER_LABELS}
    for old, new in {'Nr.':'Nr.', 'Geschl.(w/m)':'Geschlecht', 'Geschlecht (w/m)':'Geschlecht',
            'Alter':'Alter (Jahre)', 'Körpergröße (cm)':'Körperlänge (cm)', 'Körpergewicht (kg)':'Gewicht (kg)',
            'Fasertyp':'Typ', 'Entwicklung':'Entwicklungsstand', 'Shuttle: Gesamtstrecke (m)':'Gesamtstrecke',
            'Datum':'Datum', 'Testbezeichnung':'Testbezeichnung', 'Team':'Team', 'Kaderbereich':'Kaderbereich',
            'Schwerpunkt':'Schwerpunkt', 'Zuordnung':'Zuordnung', '60 m (s)':'60 m (s)'}.items():
        aliases[roster_header(old)] = new
    header_index = next((i for i, row in enumerate(table[:10]) if any(roster_header(v)=='name' for v in row)), None)
    if header_index is None:
        raise ValueError('Keine Namensspalte in den ersten zehn Zeilen gefunden.')
    raw_headers = list(table[header_index])
    while raw_headers and not field_text(raw_headers[-1]):
        raw_headers.pop()
    headers = [aliases.get(roster_header(v)) for v in raw_headers]
    if None in headers or len(set(headers)) != len(headers):
        raise ValueError('Unbekannte oder doppelte Spaltenüberschriften: ' + ', '.join(field_text(v) for v,h in zip(raw_headers,headers) if h is None))
    metadata = {'datum':None,'team':'','title':'Leistungsanalyse','focus':None}
    dates, teams, titles, focuses = set(), set(), set(), set()
    for row in table[:header_index]:
        for col, value in enumerate(row[:-1]):
            key = roster_header(value)
            following = row[col+1]
            if not field_text(following) or isinstance(following, dict):
                continue
            if key == 'datum':
                dates.add(field_date(following))
            elif key == 'team':
                teams.add(field_text(following))
            elif key == 'schwerpunkt':
                focuses.add(roster_focus(following))
    rows = []
    for line, values in enumerate(table[header_index+1:], header_index+2):
        record = dict(zip(headers, values))
        for key,value in list(record.items()):
            if isinstance(value,str) and value.startswith("'") and value[1:].lstrip().startswith(('=','+','-','@')):
                record[key] = value[1:]
        name = field_text(record.get('Name'))
        meaningful = any(field_text(v) for k,v in record.items() if k not in ('Nr.','Gesamtstrecke'))
        if not meaningful:
            continue
        if not name or len(name) > 120:
            raise ValueError(f'Zeile {line}: Name fehlt oder ist zu lang.')
        if any(field_text(v) for v in values[len(headers):]):
            raise ValueError(f'Zeile {line}: Werte ohne Spaltenüberschrift.')
        for key, value in record.items():
            if key != 'Gesamtstrecke' and (isinstance(value, dict) or (isinstance(value,str) and value.startswith('='))):
                raise ValueError(f'Zeile {line}, {key}: Bitte einen eingetragenen Wert statt einer Formel verwenden.')
        row = {label:field_text(record.get(label)) for label in ROSTER_LABELS}
        if record.get('60 m (s)') not in (None,''):
            if row['Sprintzeit (s)'] or row['Sprintstrecke (m)']:
                raise ValueError(f'Zeile {line}: 60-m-Zeit und variable Sprintangabe bitte nicht doppelt verwenden.')
            row['Sprintzeit (s)'] = field_text(record['60 m (s)'])
            row['Sprintstrecke (m)'] = '60'
        total = record.get('Gesamtstrecke')
        row['Gesamtstrecke zur Kontrolle'] = '' if isinstance(total,dict) or field_text(total).startswith('=') else field_text(total)
        row['Zuordnung'] = field_match(name, field_text(record.get('Kaderbereich')), identities) or ROSTER_NEW
        row['Quellzeile'] = str(line)
        for key, values_set in [('Datum',dates),('Team',teams),('Testbezeichnung',titles),('Schwerpunkt',focuses)]:
            if field_text(record.get(key)):
                values_set.add(field_date(record[key]) if key=='Datum' else roster_focus(record[key]) if key=='Schwerpunkt' else field_text(record[key]))
        rows.append(row)
    if not rows or len(rows) > FIELD_MAX_ROWS:
        raise ValueError('Bitte 1 bis 1000 Personen in einer Datei erfassen.')
    if any(len(values) > 1 for values in (dates,teams,titles,focuses)):
        raise ValueError('Eine Tabelle darf nur ein Team, Testdatum, einen Schwerpunkt und eine Testbezeichnung enthalten.')
    metadata.update(datum=next(iter(dates),None),team=next(iter(teams),''),title=next(iter(titles),'Leistungsanalyse'),focus=next(iter(focuses),None))
    return rows, metadata


def roster_focus(value):
    normalized = roster_header(value)
    if normalized in ('komplex','fussball1','fuball1komplextraining','fussball1komplextraining'):
        return 'komplex'
    if normalized in ('speedjump','fussball2','fuball2speedandjump','fussball2speedandjump'):
        return 'speed_jump'
    raise ValueError('Schwerpunkt: Fußball 1 – Komplextraining oder Fußball 2 – Speed and Jump auswählen.')


def roster_enum(value, label, choices):
    normalized = roster_header(value)
    if not normalized:
        return None
    if normalized not in choices:
        raise ValueError(f'{label}: unbekannte Angabe „{field_text(value)}“.')
    return choices[normalized]


def prepare_roster_batch(kader, rows, datum, bogen, focus, team='', correct=False, use_reference=True, default_mode='Nicht angegeben'):
    datum = field_date(datum)
    if focus not in FOCUS_LABELS or not field_text(bogen) or len(bogen) > 120 or len(team) > 120:
        raise ValueError('Schwerpunkt, Team oder Testbezeichnung prüfen.')
    if not rows or len(rows) > FIELD_MAX_ROWS:
        raise ValueError('Bitte 1 bis 1000 Personen erfassen.')
    updated = validate_kader(kader)
    identities = field_identity_map(updated)
    seen, previews, errors = set(), [], []
    changed = 0
    for index, row in enumerate(rows, 1):
        try:
            source_name = field_text(row.get('Name'))
            if not source_name or len(source_name) > 120:
                raise ValueError('Name fehlt oder ist zu lang.')
            identity = row.get('Zuordnung', ROSTER_NEW)
            if identity == ROSTER_NEW:
                matches = [p for p in identities.values() if field_name_key(p[1]) == field_name_key(source_name)]
                if matches:
                    raise ValueError('Dieser Name ist bereits vorhanden. Bitte die vorhandene Person zuordnen.')
                sport, name = 'Fussball', source_name
                old = None
            elif identity in identities:
                sport, name = identities[identity]
                old = updated[sport][name]
            else:
                raise ValueError('Bitte eine gültige Person zuordnen oder „Neues Profil anlegen“ wählen.')
            name_key = (sport, field_name_key(name))
            if name_key in seen:
                raise ValueError('Diese Person ist mehrfach in der Tabelle vorhanden.')
            seen.add(name_key)
            values = {
                'alter':roster_number(row.get('Alter (Jahre)'), 'Alter',9,40,True),
                'gewicht':roster_number(row.get('Gewicht (kg)'), 'Gewicht (kg)',30,140),
                'groesse':roster_number(row.get('Körperlänge (cm)'), 'Körperlänge (cm)',130,215),
                'geschlecht':roster_enum(row.get('Geschlecht'),'Geschlecht',{'w':'Weiblich','weiblich':'Weiblich','m':'Männlich','mannlich':'Männlich'}),
                'fasertyp':roster_enum(row.get('Typ'),'Typ',{'ausdauer':'Ausdauer','kraft':'Kraft','sprungkraft':'Sprungkraft','gazelle':'Gazelle','sprint':'Schnelligkeit (Sprint)','schnelligkeitsprint':'Schnelligkeit (Sprint)'}),
                'reife':roster_enum(row.get('Entwicklungsstand'),'Entwicklungsstand',{'normal':'Normalentwickler','normalentwickler':'Normalentwickler','spatentwickler':'Spätentwickler (Retardiert)','retardiert':'Spätentwickler (Retardiert)','spatentwicklerretardiert':'Spätentwickler (Retardiert)','fruhentwickler':'Frühentwickler (Akzeleriert)','akzeleriert':'Frühentwickler (Akzeleriert)','fruhentwicklerakzeleriert':'Frühentwickler (Akzeleriert)'})}
            if values['groesse'] is not None:
                values['groesse'] = round(values['groesse']/100,4)
            band_value = 'Master' if field_text(row.get('Altersklasse')).upper() in ('Ü23','Ü 23','ÜBER 23','23+') else row.get('Altersklasse')
            band = roster_enum(band_value, 'Altersklasse', {**{b.lower():b for b in ('U11','U13','U15','U17','U20','U23')},'u23plus':'MASTER','master':'MASTER','erwachsene':'MASTER'})
            # NFKD strips the umlaut; Ü23 must not be confused with U23.
            if field_text(row.get('Altersklasse')).upper() in ('Ü23','Ü 23','ÜBER 23','23+'):
                band = 'MASTER'
            frequency = roster_number(row.get('TE pro Woche'), 'TE pro Woche',1,2,True)
            if old is None and (any(v is None for v in values.values()) or band is None or frequency is None):
                raise ValueError('Für ein neues Profil bitte Alter, Geschlecht, Altersklasse, Gewicht, Körperlänge, Typ, Entwicklungsstand und TE pro Woche ausfüllen.')
            rec = deepcopy(old) if old else {'t_60':None,'sbe':'SR 2'}
            rec.update({k:v for k,v in values.items() if v is not None})
            band = band or rec['profil'].split('_')[1]
            gender = rec.get('geschlecht', 'Weiblich' if rec.get('profil','').endswith('_w') else 'Männlich')
            profile = football_profile('Fussball_'+band, gender)
            rec['profil'] = storage_profile(profile, sport)
            settings = {key:focus_settings(rec,key) for key in FOCUS_LABELS}
            active = settings.setdefault(focus, {'planung':{}})
            if frequency is not None:
                active.setdefault('planung',{})['einheiten'] = frequency
            rec['trainingsschwerpunkt'] = focus
            rec['planung'] = deepcopy(active.get('planung',{}))
            # Keep other planning fields while resetting parameters tied to a changed age band.
            if old and old['profil'].split('_')[1] != band:
                rec['m_training'] = m_training_defaults(sport,band)
                for config in settings.values():
                    config['m_training'] = m_training_defaults('Fussball',band)
                    config['hurdles'] = {}
                    config['hurdles_band'] = band
                    if config.get('speed_jump'):
                        config['speed_jump'] = normalize_speed_jump(config['speed_jump'],band,gender)
            rec['fussball_schwerpunkte'] = settings
            if team:
                rec['team'] = team
            distance = roster_number(row.get('Sprintstrecke (m)'), 'Sprintstrecke (m)',.01,10000)
            seconds = field_number(row.get('Sprintzeit (s)'), 'Sprintzeit (s)')
            if seconds is not None and distance is None:
                raise ValueError('Zur Sprintzeit fehlt die Sprintstrecke.')
            if use_reference and distance == 60 and seconds is not None:
                if not 6 <= seconds <= 15:
                    raise ValueError('Die Trainingsreferenz verlangt 6 bis 15 s über 60 m. Referenzübernahme ausschalten, um nur den Test zu speichern.')
                rec['t_60'] = seconds
                if rec.get('t_150_quelle','berechnet') == 'berechnet':
                    rec['t_150'] = round(seconds*2.375,2)
                    rec['t_150_quelle'] = 'berechnet'
            diffs = []
            if old:
                for key in ('alter','gewicht','groesse','geschlecht','fasertyp','reife','profil','trainingsschwerpunkt','team','t_60'):
                    if rec.get(key) != old.get(key):
                        diffs.append(f'{key}: {old.get(key, "leer")} → {rec.get(key, "leer")}')
                previous_frequency = focus_settings(old,focus).get('planung',{}).get('einheiten',1)
                if frequency is not None and frequency != previous_frequency:
                    diffs.append(f'TE/Woche: {previous_frequency} → {frequency}')
                if diffs and not correct:
                    raise ValueError('Abweichende Stammdaten: ' + '; '.join(diffs) + '. Zum Übernehmen die Korrekturoption wählen.')
            updated[sport][name] = rec
            testrow = field_empty_row(name, f'{name} [{sport}]')
            for label in ('Shuttlezeit (s)','5er-Hop links (m)','5er-Hop rechts (m)','5er-Schlusssprung (m)','Shuttle-Angabe','Notiz'):
                testrow[label] = field_text(row.get(label))
            if seconds is not None:
                testrow['60 m (s)' if distance == 60 else 'Sprintzeit (s)'] = str(seconds)
                testrow['Sprintstrecke (m)'] = str(distance)
            # Validate provided arrangement even when its measurement is still blank.
            way = roster_number(row.get('Shuttle: einfache Strecke (m)'), 'Strecke je Weg',.01,10000)
            count = roster_number(row.get('Shuttle-Anzahl (1/2/3)'), 'Shuttle-Anzahl',1,3,True)
            extra = roster_number(row.get('Wendezuschlag gesamt (m)'), 'Wendezuschlag gesamt (m)',0,1000) or 0
            config = shuttle_definition(next(k for k,v in SHUTTLE_FORMS.items() if v==count),way,extra) if way is not None and count is not None else None
            total = roster_number(row.get('Gesamtstrecke zur Kontrolle'), 'Gesamtstrecke',.01,61000)
            if total is not None and (config is None or not math.isclose(total,way*2*count+extra,abs_tol=.001)):
                raise ValueError('Gesamtstrecke passt nicht zu einfacher Strecke, Shuttle-Anzahl und Wendezuschlag.')
            has_results = any(field_text(testrow.get(label)) for label in FIELD_METRICS.values())
            test_preview = {}
            if has_results:
                updated, test_rows, _, _ = prepare_field_batch(updated,[testrow],datum,bogen,correct=correct,shuttle=config,default_mode=default_mode)
                test_preview = test_rows[0]
                rec = updated[sport][name]
            # Retain documented planned distances, including rows awaiting results.
            protocol = {label:field_text(row.get(label)) for label in ROSTER_LABELS if field_text(row.get(label))}
            import_id = hashlib.sha256(json.dumps([datum,bogen.casefold()],ensure_ascii=False).encode()).hexdigest()
            imports = rec.setdefault('tabellenimporte', {})
            previous = imports.get(import_id)
            entry = {'datum':datum,'bogen':bogen,'team':team,'angaben':protocol}
            if previous != entry:
                imports[import_id] = entry
            rec_changed = old is None or rec != old
            changed += rec_changed
            notice = '; '.join(diffs)
            if not age_matches_profile(rec['alter'],rec['profil']):
                notice += '; Alter und Trainingsklasse bitte prüfen'
            if rec.get('t_60') is None:
                notice += '; 60-m-Trainingsreferenz noch offen'
            previews.append({'Person':name,'Aktion':'Neu anlegen' if old is None else 'Aktualisieren' if rec_changed else 'Bereits gespeichert',
                'Alter':rec['alter'],'Geschlecht':gender,'Altersklasse':'Ü23 / Master' if band=='MASTER' else band,
                'kg':rec['gewicht'],'cm':round(rec['groesse']*100,2),'Typ':rec['fasertyp'],'Entwicklung':rec['reife'],
                'TE/Woche':rec['planung'].get('einheiten',1),'Schwerpunkt':FOCUS_LABELS[focus],
                'Sprint (m)':distance,'Sprint (s)':seconds,'Shuttle-Test':shuttle_description(config) if config else '',
                **{k:v for k,v in test_preview.items() if k in ('Shuttlezeit (s)','5er-Hop links (m)','5er-Hop rechts (m)','5er-Schlusssprung (m)','Shuttle-Angabe')},
                'Hinweise':notice.strip('; ')})
        except (ValueError,TypeError) as exc:
            errors.append(f'Zeile {row.get("Quellzeile",index)} ({field_text(row.get("Name"))}): {exc}')
    if errors:
        raise ValueError('\n'.join(errors[:30]))
    return validate_kader(updated), previews, changed


def roster_csv(rows, datum, bogen, team, focus, identities=None):
    stream = io.StringIO(newline='')
    labels = ['Datum','Testbezeichnung','Team','Schwerpunkt','Kaderbereich',*ROSTER_LABELS]
    writer = csv.DictWriter(stream,labels,delimiter=';',lineterminator='\n')
    writer.writeheader()
    for row in rows:
        values = {'Datum':datum,'Testbezeichnung':bogen,'Team':team,'Schwerpunkt':FOCUS_LABELS[focus],
                  **{k:field_text(row.get(k)) for k in ROSTER_LABELS}}
        identity = (identities or {}).get(row.get('Zuordnung'))
        values['Kaderbereich'] = identity[0] if identity else ''
        if identity:
            values['Name'] = identity[1]
        values = {k:"'"+v if v.lstrip().startswith(('=','+','-','@')) else v for k,v in values.items()}
        writer.writerow(values)
    return stream.getvalue().encode('utf-8-sig')


def roster_sync_grid(key):
    draft = deepcopy(st.session_state.get('roster_draft',[]))
    for index, changes in st.session_state.get(key,{}).get('edited_rows',{}).items():
        if 0 <= int(index) < len(draft):
            for label, value in changes.items():
                if label in ROSTER_LABELS or label == 'Zuordnung':
                    draft[int(index)][label] = field_text(value)
    st.session_state.roster_draft = draft


def render_roster_import():
    st.button('Zur Trainingsplanung', on_click=navigiere, args=('Operativ',))
    st.caption('Stammdaten und Testergebnisse gemeinsam aus Excel, LibreOffice oder CSV übernehmen. Erst laden, kontrollieren, dann gemeinsam speichern. Ein PDF oder Foto ist hier kein Tabellenimport.')
    identities = field_identity_map(st.session_state.kader_db)
    draft = st.session_state.get('roster_draft')
    with st.expander('Tabelle laden', expanded=draft is None):
        upload = st.file_uploader('Ausgefüllte Stammdaten- und Testtabelle',type=['xlsx','ods','csv'],key='roster_upload')
        allow_replace = st.checkbox('Bisherigen Tabellenentwurf ersetzen',key='roster_replace') if draft else True
        if st.button('Stammdaten-Tabelle laden',disabled=upload is None or not allow_replace):
            try:
                rows, metadata = read_roster_file(upload.getvalue(),upload.name,identities)
                st.session_state.roster_draft = rows
                st.session_state.roster_pending = metadata
                st.session_state.roster_epoch = st.session_state.get('roster_epoch',0)+1
                st.session_state.pop('roster_preview',None)
                st.rerun()
            except Exception as exc:
                st.error(f'Datei nicht geladen: {exc}')
        if st.button('Leere Erfassung für 30 Personen öffnen',disabled=not allow_replace):
            st.session_state.roster_draft = [{**{label:'' for label in ROSTER_LABELS},'Zuordnung':ROSTER_NEW} for _ in range(30)]
            st.session_state.roster_epoch = st.session_state.get('roster_epoch',0)+1
            st.session_state.pop('roster_preview',None)
            st.rerun()
    pending = st.session_state.pop('roster_pending',None)
    if pending:
        st.session_state.roster_date = date.fromisoformat(pending['datum']) if pending['datum'] else date.today()
        st.session_state.roster_team = pending['team']
        st.session_state.roster_title = pending['title']
        st.session_state.roster_focus = pending['focus'] or 'speed_jump'
        if not pending['datum']:
            st.warning('Testdatum fehlt in der Datei. Bitte unten einstellen.')
    for key, value in st.session_state.get('roster_metadata',{}).items():
        if key not in st.session_state:
            st.session_state[key] = value
    a,b = st.columns(2)
    datum = a.date_input('Testdatum der Tabelle',key='roster_date')
    team = b.text_input('Team / Trainingsgruppe',max_chars=120,key='roster_team')
    title = st.text_input('Bezeichnung des Testtermins',value='Leistungsanalyse',max_chars=120,key='roster_title')
    focus = st.selectbox('Schwerpunkt für die importierten Personen',list(FOCUS_LABELS),index=1,format_func=FOCUS_LABELS.get,key='roster_focus')
    mode = st.selectbox('Shuttlezeiten ohne Kennzeichnung übernehmen als',FIELD_SHUTTLE_MODES,index=2,key='roster_mode')
    st.caption('1 Shuttle = hin UND zurück. Gesamtstrecke = einfache Strecke × 2 × Shuttle-Anzahl + Wendezuschlag für den gesamten Test. Ü23 wird der vorhandenen Trainingsklasse Master zugeordnet.')
    st.session_state.roster_metadata = {k:st.session_state[k] for k in ('roster_date','roster_team','roster_title','roster_focus','roster_mode')}
    draft = st.session_state.get('roster_draft')
    if draft is None:
        return
    view = st.radio('Tabellenausschnitt',['Stammdaten','Lauftests','Sprungtests','Alle Angaben'],horizontal=True,key='roster_view')
    shared = ['Name','Zuordnung']
    sections = {'Stammdaten':ROSTER_LABELS[1:9],'Lauftests':ROSTER_LABELS[9:15]+['Shuttle-Angabe'],
                'Sprungtests':ROSTER_LABELS[15:18]+['Notiz'],'Alle Angaben':ROSTER_LABELS[1:]}
    epoch = st.session_state.get('roster_epoch',0)
    key = f'roster_grid_{epoch}'
    columns = {label:st.column_config.TextColumn(label,width='small' if label not in ('Name','Notiz','Entwicklungsstand') else 'medium') for label in ROSTER_LABELS}
    columns['Zuordnung'] = st.column_config.SelectboxColumn('Zuordnung',options=[ROSTER_NEW,*identities],width='medium')
    columns['Shuttle-Angabe'] = st.column_config.SelectboxColumn('Shuttle-Angabe',options=['',*FIELD_SHUTTLE_MODES])
    st.caption('Eindeutig vorhandene Namen werden zugeordnet. Bei anderer Schreibweise bitte die richtige Person auswählen, um Doppelprofile zu vermeiden. Leere Angaben ändern vorhandene Stammdaten nicht.')
    edited = st.data_editor(pd.DataFrame(draft).fillna('').astype(str),hide_index=True,width='stretch',height=450,row_height=42,
        column_order=shared+sections[view],column_config=columns,num_rows='fixed',key=key,on_change=roster_sync_grid,args=(key,))
    rows = edited.to_dict('records')
    # Ignore unused template slots, but never drop a row containing an entered value.
    rows = [r for r in rows if any(field_text(r.get(k)) for k in ROSTER_LABELS)]
    st.download_button('Erfassungsentwurf herunterladen (CSV)',roster_csv(rows,datum.isoformat(),title,team,focus,identities),file_name='Doc_Athletic_Kader_und_Tests.csv',mime='text/csv')
    correct = st.checkbox('Abweichende vorhandene Stammdaten und Testwerte übernehmen',key='roster_correct')
    use_reference = st.checkbox('Vorhandene 60-m-Testzeiten als Trainingsreferenz übernehmen',value=True,key='roster_reference')
    state = dict(rows=rows,datum=datum.isoformat(),bogen=title,focus=focus,team=team,correct=correct,use_reference=use_reference,default_mode=mode)
    fingerprint = hashlib.sha256(json.dumps(state,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if st.button('Kader und Tests prüfen',type='primary'):
        try:
            _, preview, changed = prepare_roster_batch(st.session_state.kader_db,**state)
            st.session_state.roster_preview = dict(fingerprint=fingerprint,revision=st.session_state.kader_revision,preview=preview,changed=changed)
        except ValueError as exc:
            st.session_state.pop('roster_preview',None)
            st.error(str(exc))
    checked = st.session_state.get('roster_preview')
    if checked and checked['fingerprint'] == fingerprint:
        st.subheader('Kontrolle vor der Übernahme')
        st.dataframe(pd.DataFrame(checked['preview']),hide_index=True,width='stretch')
        st.caption(f"{len(checked['preview'])} Personen geprüft; {checked['changed']} mit Änderungen. Fehlende Testergebnisse bleiben leer. Andere Profile und bisherige Trainingsverläufe bleiben erhalten.")
        if st.button('Geprüften Kader und Tests gemeinsam speichern',disabled=not checked['changed'],type='primary'):
            try:
                if checked['revision'] != st.session_state.kader_revision:
                    raise StorageConflict('Der Kader hat sich seit der Prüfung geändert. Bitte erneut prüfen.')
                candidate, _, changed = prepare_roster_batch(st.session_state.kader_db,**state)
                revision = speichere_kader_in_datei(candidate,checked['revision'])
                st.session_state.kader_db = candidate
                st.session_state.kader_revision = revision
                st.session_state.edit_epoch = st.session_state.get('edit_epoch',0)+1
                identities_after = field_identity_map(candidate)
                for row in rows:
                    if row.get('Zuordnung') == ROSTER_NEW:
                        row['Zuordnung'] = field_match(row['Name'],'Fussball',identities_after)
                st.session_state.roster_draft = rows
                st.session_state.roster_epoch = epoch+1
                st.session_state.pop('roster_preview',None)
                st.session_state.save_notice = f'Kader und Tests für {changed} Personen gespeichert. Bitte anschließend eine Kader-Sicherung herunterladen.'
                st.rerun()
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:
                st.error(f'Nichts gespeichert: {exc}')
    elif checked:
        st.info('Eingaben wurden geändert. Bitte erneut prüfen.')


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
            'Die Übungen eines Blocks nacheinander im Staffelbetrieb absolvieren. '
            'Anschließend der zugehörige Lauf- oder Techniktransfer. Lohnende Pause durch Partnerwechsel. ')
    if frequency == 1:
        text += 'Eine vollständige Einheit mit den vorgesehenen Kraft-, Koordinations- und Schnelligkeitsanteilen.'
    else:
        text += (f'Haupteinheit mit {config.get("main_sets", 4)} Sätzen an den Kraftstationen; '
                 f'kürzere zweite Einheit mit Schwerpunkt Schnelligkeit und Reaktivität. '
                 f'Planungsabstand: {config.get("gap_days", 3)} Tage zwischen den Einheiten. '
                 'Erwärmung und ihre integrierten Beschleunigungs- und Technikanteile bleiben in beiden Einheiten.')
    return text + " " + PARTNER_ORGANIZATION

def organization_ui(saved, frequency, key, disabled=False, focus="komplex"):
    config = deepcopy(saved or {})
    st.caption('Standard: eine zusätzliche Athletikeinheit pro Woche neben dem Sporttraining. Die Aufteilung greift erst bei zwei gewählten Einheiten.')
    config['group_size'] = st.number_input('Personen je Minigruppe', 3, 5, int(config.get('group_size', 4)), key=key+'group', disabled=disabled)
    if frequency == 2:
        if focus == "komplex":
            config['main_sets'] = st.number_input('Sätze an Kraftstationen der Haupteinheit', 4, 5, int(config.get('main_sets', 4)), key=key+'sets', disabled=disabled)
        config['gap_days'] = st.number_input('Tage zwischen den beiden Athletikeinheiten', 1, 7, int(config.get('gap_days', 3)), key=key+'gap', disabled=disabled)
    st.caption(organization_text(frequency, config) if focus == "komplex" else "Speed and Jump: kurze Qualitätsblöcke; der Plan führt die Sätze je Übung auf. Erwärmung und sportartspezifischer Anschluss bleiben erhalten.")
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
        if "schwerpunkt" in item and item["schwerpunkt"] not in FOCUS_LABELS:
            raise ValueError("Unbekannter Schwerpunkt im Protokoll.")
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

def save_unit_record(record, cycle, te, plan, source, actual=None, notes=None, performed=None, timing=None, focus=None):
    updated = deepcopy(record)
    sessions = updated.setdefault("einheitenprotokoll", {})
    key = focus_unit_key(record, cycle, te, focus)
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
    if focus is not None:
        item["schwerpunkt"] = focus
        updated["trainingsschwerpunkt"] = focus
    sessions[key] = item
    validate_sessions(sessions)
    return updated

def next_recommendations(record, cycle, te, metric, percent, focus=None):
    # Zeitangaben sind ausdrücklich keine Last-/Wiederholungsprogression.
    if metric not in ("Last (kg)", "Wdh. je Satz/Seite", "Strecke (m)") or not 0 <= percent <= 20:
        raise ValueError("Ungültige Steigerungseinstellung.")
    latest = {}
    entries = sorted(record.get("einheitenprotokoll", {}).values(), key=lambda x: (x.get("performed", ""), x.get("saved_at", "")))
    for item in entries:
        if focus is not None and item.get("schwerpunkt", legacy_focus(record)) != focus:
            continue
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

def unit_workflow(athlete, sport, target, te, default_plan, key_for, guest, default_timing=None, focus="komplex", profile_for_save=None):
    cycle=athlete.get("aktiver_makrozyklus", "Bestand")
    unit_key=focus_unit_key(athlete,cycle,te,focus)
    saved=athlete.get("einheitenprotokoll",{}).get(unit_key)
    prefix=key_for("protocol_"+hashlib.sha256(unit_key.encode()).hexdigest()[:10])
    st.subheader(f"TE {te}: {FOCUS_LABELS[focus]} – Plan und Durchführung")
    st.caption("Minigruppen mit vergleichbaren Voraussetzungen. Übungen im Block erhalten; danach das zugehörige Laufprogramm. Lohnende Pause durch Partnerwechsel.")
    if focus == "komplex":
        st.caption("Team-Style: etwa 2 Meter Abstand; Führung nach aktueller Leistungsfähigkeit, Wechsel nach Abstimmung.")
    sources=["Generierter Plan: " + FOCUS_LABELS[focus]]+list(st.session_state.get("private_sources", SOURCE_UNITS))
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
    recs=next_recommendations(athlete,cycle,te,metric,pct,focus)
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
    st.caption("Soll- und Ist-Speichern sichern auch die aktuell eingetragenen Profilwerte und Schwerpunktvorgaben dieser Person.")
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
            profile = profile_for_save() if profile_for_save is not None else updated[sport][target]
            rec=save_unit_record(profile,cycle,te,saved["plan"] if save_actual else plan,saved["source"] if save_actual else source,
                                actual=rows,notes=notes if save_actual else None,performed=performed.isoformat() if save_actual else None, timing=timing_actual if save_actual else timing_plan,focus=focus)
            rec["folge_rate"]=pct
            updated[sport][target]=rec
            revision=speichere_kader_in_datei(updated,st.session_state.kader_revision)
            st.session_state.kader_db=updated;st.session_state.kader_revision=revision
            st.session_state.edit_epoch=st.session_state.get("edit_epoch",0)+1
            st.session_state.save_notice="Sollplan und aktuelle Profilwerte gespeichert." if save_plan else "Ist-Durchführung und aktuelle Profilwerte gespeichert; Folgeempfehlungen stehen bei der nächsten Einheit bereit."
            st.rerun()
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:
            st.error(f"Einheit nicht gespeichert: {exc}")
    if saved:
        report="<!doctype html><html lang='de'><meta charset='utf-8'><title>Einheitenprotokoll</title><style>body{font-family:Arial}pre{white-space:pre-wrap}td,th{border:1px solid #999;padding:5px}table{border-collapse:collapse}</style>"
        report+=f"<h1>{escape(target)} – {escape(cycle)} – TE {te}</h1><p>{escape(FOCUS_LABELS[focus])}</p><h2>Gespeicherter Sollplan</h2><pre>{escape(saved['plan'])}</pre>"
        report+=timing_html(saved.get("timing", {}))
        report+="<h2>Tatsächliche Durchführung</h2>"+pd.DataFrame(saved["actual"],columns=PROTOCOL_COLUMNS).to_html(index=False,escape=True,na_rep="—")
        report+=f"<p>{escape(saved.get('performed',''))}</p><pre>{escape(saved.get('notes',''))}</pre></html>"
        st.download_button("Soll-/Ist-Protokoll herunterladen",report,file_name=f"Modul1_TE{te}_Protokoll.html",mime="text/html",key=prefix+"download")


"""Modul 1 Version 115: explicit coach-defined reference calculation, no telemetry control."""
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
                               'Ab U17 keine automatische Ballform; bestehende individuelle Vorgaben bleiben erhalten.')
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
                     'Pause': PARTNER_PAUSE,
                     'Fokus': technique + ' ' + ball['notes']})
    maximum = config['maximal']
    if maximum['enabled'] and te in maximum['units'] and (frequency == 1 or short_day):
        rows.append({'Block': 'M-Sprint ohne Ball', 'Trainingsmittel': 'M-Sprints ohne Ball · maximales Eins-gegen-eins',
                     'Sätze': f"{maximum['series']} Serien", 'Wdh_oder_Strecke': m_distance_text(maximum),
                     'Zusatzlast': 'ohne Ball / ohne Zusatzlast', 'Intensität': 'Maximal; enge Richtungswechsel',
                     'Pause': PARTNER_PAUSE,
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


def validate_plan_settings(plan):
    if not isinstance(plan, dict):
        raise ValueError("Ungültige Planung.")
    validate_organization(plan.get("organisation", {}))
    ranges = {"einheiten":(1,2), "startwoche":(1,52), "bag_start":(1,20),
              "burpee_start":(1,30), "cheer_start":(0,30), "single_start":(0,30), "beid_start":(0,30),
              "kreuzheben_last":(0,500), "bag_last":(0,30), "test_distanz":(50,1500), "test_zeit":(0,900),
              "test_prozent":(50,100), "steigerung_wdh":(0,5), "abc_step":(0,10), "abc_start_m":(10,15)}
    for key, (low, high) in ranges.items():
        value = plan.get(key)
        if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high):
            raise ValueError(f"Ungültige Planung: {key}.")
        if value is not None and key not in ("bag_last", "test_zeit", "kreuzheben_last", "abc_step", "abc_start_m") and int(value) != value:
            raise ValueError(f"Ganze Zahl erforderlich: {key}.")
    for key in ("progression", "kapazitaet20", "burpees_bestaetigt", "tempo_interpolation", "tempo_extrapolation"):
        if key in plan and type(plan[key]) is not bool:
            raise ValueError(f"Ungültige Freigabe: {key}.")
    if "rolle" in plan and plan["rolle"] not in ["Automatisch nach Wochenrhythmus", "Haupttag", "Neuromuskulär / vor dem Spiel"]:
        raise ValueError("Unbekanntes Einheitsziel.")


def validate_kader(kader):
    sports = {"Fussball", "Leichtathletik"}
    if not isinstance(kader, dict) or not kader or not set(kader) <= sports:
        raise ValueError("Die Sicherung muss eine Fußball-Kaderliste oder einen unterstützten Altbestand enthalten.")
    # Older backups can contain just one sport. Complete the internal structure
    # without creating athletes or changing the supplied backup.
    kader = deepcopy(kader)
    for sport in ("Fussball", "Leichtathletik"):
        kader.setdefault(sport, {})
    for sport, athletes in kader.items():
        if not isinstance(athletes, dict) or len(athletes) > 10000:
            raise ValueError("Ungültige Athletenliste.")
        for name, p in athletes.items():
            if not isinstance(name, str) or not name.strip() or len(name) > 120 or name != name.strip():
                raise ValueError("Ungültiger Athletenname.")
            if not isinstance(p, dict):
                raise ValueError("Ungültiges Athletenprofil.")
            for field, low, high in [("alter",9,40),("groesse",1.30,2.15),("gewicht",30,140),("t_60",6,15)]:
                value = p.get(field)
                if field == "t_60" and "t_60" in p and value is None:
                    continue
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
            validate_field_tests(p.get("feldtests", []))
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
            validate_plan_settings(p.get("planung", {}))
            if p.get("trainingsschwerpunkt", "komplex") not in FOCUS_LABELS:
                raise ValueError("Unbekannter Fußball-Schwerpunkt.")
            settings = p.get("fussball_schwerpunkte", {})
            if not isinstance(settings, dict) or set(settings) - set(FOCUS_LABELS):
                raise ValueError("Ungültige Schwerpunktplanung.")
            for config in settings.values():
                if not isinstance(config, dict) or set(config) - {"planung", "m_training", "speed_jump", "hurdles", "hurdles_band"}:
                    raise ValueError("Ungültige Schwerpunktvorgaben.")
                validate_plan_settings(config.get("planung", {}))
                if config.get("hurdles"):
                    if config.get("hurdles_band", p["profil"].split("_")[1]) not in M_HURDLE_EDGES:
                        raise ValueError("Altersklasse der Hürdenplanung prüfen.")
                    validate_hurdles(config["hurdles"], config.get("hurdles_band", p["profil"].split("_")[1]))
                validate_m_training(config.get("m_training", {}), "Fussball", p["profil"].split("_")[1])
                validate_speed_jump(config.get("speed_jump", {}), p["profil"].split("_")[1], p.get("geschlecht", "Weiblich" if p["profil"].endswith("_w") else "Männlich"))
    return kader


def restore_kader_backup(backup, current):
    """Replace only the sports explicitly included in a validated backup."""
    restored = validate_kader(backup)
    result = validate_kader(current)
    for sport in backup:
        result[sport] = restored[sport]
    return result

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

def organize_multisport_html(html, frequency, short_day, main_sets, sport, band, config, timing, focus="komplex", block_one_rounds=None):
    parser = MatrixRowsParser(); parser.feed(html)
    if not parser.rows: return html
    warm, hurdles, stations, running, cool = [], [], [], [], []
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
        elif row[0] == 'Speed: Hürdenumfang je Einheit': hurdles.append(row)
        elif row[0] == 'Cool-Down': cool.append(row)
        elif 'Lauf / Transfer' in row[0] or 'GLA Vorab' in row[0]:
            running.append(row)
        elif row[0] == 'M-Sprint ohne Ball':
            if frequency == 1 or short_day or focus == "speed_jump":
                running.append(row)

        else:
            if row[1].startswith('Komplextransfer: Hürdensprünge'):
                continue  # Hurdle station and short running transfer are already explicit rows.
            if focus != 'speed_jump' and frequency == 2 and not short_day and row[0] == 'Komplex: Hürden':
                continue  # Dedicated hurdle station belongs to the second session.
            row[6] = PARTNER_PAUSE
            if frequency == 2 and not short_day and focus != 'speed_jump': row[2] = main_sets
            stations.append(row)
    paired_blocks = focus == "speed_jump" and not short_day and band not in ("U11", "U13")
    if paired_blocks:
        expanded = []
        for row in stations:
            if row[1] == "Umsatz / Ausstoß-Jumps & Crunches":
                for label in ("Umsatz / Ausstoß-Jumps", "Einwurf-Crunches"):
                    separate = list(row)
                    separate[1] = label
                    expanded.append(separate)
            else:
                expanded.append(row)
        stations = expanded
    # Divide the ordered exercises into blocks of 3–5 where possible. Do not multiply
    # the running prescription when more than one block is present.
    import re
    count = 2 if paired_blocks else max(1, math.ceil(len(stations)/5))
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
        if row[0] == 'Speed Block 1: Lauf / Transfer':
            transfers[0].append(row)
        elif paired_blocks and row[0] == 'M-Sprint ohne Ball':
            transfers[0].append(row)
        elif row[0] == 'Speed Block 2: Lauf / Transfer' or prescription.startswith('Tempolauf-Aufbau:'):
            transfers[-1].append(row)
        elif match and int(match[1]) >= count:
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
    rows = list(warm) + hurdles
    for i, (group, transfer) in enumerate(zip(groups, transfers), 1):
        if paired_blocks:
            # Repetition field explicitly denotes circuit rounds, not extra sets.
            rounds = next((int(row[2].split()[0]) for row in transfer if row[0].startswith("Speed Block")), block_one_rounds if i == 1 and block_one_rounds else 3)
            for row in group:
                row[2] = f"1 Satz je Durchgang; {rounds} insgesamt"
                if rounds == 2:
                    row[3] = row[3].replace("8–6–5", "8–6").replace("(3 Sätze)", "(2 Durchgänge)")
                else:
                    row[3] = row[3].replace("(3 Sätze)", "(3 Durchgänge)")
                row[6] = PARTNER_PAUSE
        rows.extend(group)
        for row in transfer:
            row[0] = f'Block {i}: nach jedem Stationsdurchgang' if paired_blocks else f'Nach Block {i}: Lauf / Transfer'
        rows.extend(transfer)
    rows.extend(cool)
    def render(row):
        color = '#fff2cc' if row in warm else '#f2f2f2' if row in cool else '#ddebf7' if row[0].startswith('Nach Block') else '#fce4d6'
        return '<tr style="background:'+color+';color:#111">'+''.join('<td style="padding:6px;border:1px solid #aaa">'+escape(str(cell))+'</td>' for cell in row)+'</tr>'
    body = ''.join(render(row) for row in rows)
    start, end = html.index('<tbody>')+len('<tbody>'), html.index('</tbody>')
    html = html[:start]+body+html[end:]
    note = '<p>'+escape(organization_text(frequency, config) if focus == 'komplex' else ('Speed and Jump: Stations- und Laufdurchgänge. Erwärmung bleibt enthalten; Die belasteten Kraftübungen folgen ihrer Phasenplanung.' if paired_blocks else 'Speed and Jump: kurze Qualitätsblöcke mit vollständiger Erholung. Erwärmung bleibt enthalten; Die belasteten Kraftübungen folgen ihrer Phasenplanung. Die Laufvorgabe gilt insgesamt je Einheit.'))+'</p>'
    if focus == 'komplex' and sport in ('Fussball', 'Leichtathletik'):
        note += '<p>Team-Style beim vorgesehenen Lauftransfer: 3–5 Personen, etwa 2 m Abstand; Führung nach aktueller Leistungsfähigkeit, Wechsel nach Abstimmung.</p>'
    if paired_blocks:
        note += '<p>Zwei Blöcke: pro Durchgang die Stationen nacheinander je einmal, anschließend die zugeordneten Läufe. Danach folgt der nächste Durchgang desselben Blocks. Erst nach Abschluss aller Durchgänge zu Block 2 wechseln. Die angegebenen Gehstrecken bleiben Teil des Laufablaufs; lohnende Pause durch Partnerwechsel. Die angegebenen Gesamtmeter werden nicht erneut multipliziert.</p>'
    note += '<p>'+escape(PARTNER_PAUSE + '. ' + PARTNER_ORGANIZATION)+'</p>'
    if hurdles:
        note += '<p>Hürdenumfang einmal je Einheit: einbeinige Durchgänge vollständig links und rechts; keine zusätzliche Multiplikation mit Stationen, Blockrunden oder aufgebauten Reihen.</p>'
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
    st.title("Doc Athletic Train Smart Evolution Software 115")
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
        st.markdown("<p style='text-align: center; color: #c5c6c7; margin-top: 20px;'>Bitte Zugriffscode eingeben (Fußball 1 – Komplextraining / Fußball 2 – Speed and Jump)</p>", unsafe_allow_html=True)
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
    if st.session_state.get("navigations_status") == "Testtabelle" and "field_current_rows" in st.session_state:
        st.session_state.field_draft = deepcopy(st.session_state.field_current_rows)
        st.session_state.field_epoch = st.session_state.get("field_epoch",0)+1
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
    st.sidebar.caption('Auch reine Fußball-Sicherungen sind möglich. Enthaltene Kaderbereiche werden ersetzt; nicht enthaltene bleiben unverändert.')
    restore_confirm = st.sidebar.checkbox('Enthaltene Kaderdaten durch die Sicherung ersetzen')
    if _upload is not None and st.sidebar.button('Backup jetzt wiederherstellen', disabled=not restore_confirm):
        try:
            if _upload.size > 5_000_000:
                raise ValueError("Die Sicherung ist zu groß.")
            restored = restore_kader_backup(json.loads(_upload.getvalue()), st.session_state.kader_db)
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

if st.session_state.auth_modus == "trainer":
    st.sidebar.button("TESTTABELLE / DATEIIMPORT", on_click=navigiere, args=("Testtabelle",))

if st.sidebar.button("ABMELDEN"):
    st.session_state.clear()
    st.rerun()

if st.session_state.auth_modus == "gast":
    st.sidebar.warning("GAST-MODUS (Nur Leserechte)")

st.caption('Version 115 · Stand ' + BUILD_STAND)

if st.session_state.navigations_status == 'Start':
    st.markdown("<h1 style='text-align: center; color: #66fcf1 !important; margin-top: 30px;'>DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE 115</h1><p style='text-align:center'>Modul 1 · Version 115 · Grundlast → Jumps → Sprünge · Tempotabellen bis 800 m</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #c5c6c7; font-size: 16px;'>Fußball 1 – Komplextraining / Fußball 2 – Speed and Jump · Individuelle Trainingsplanung</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lade_bild(["logo.png", "logo.png.png", "logo"], use_col=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("SYSTEM INITIALISIEREN >>", on_click=navigiere, args=('Uebersicht',))

elif st.session_state.navigations_status == 'Uebersicht':
    st.title("Systemübersicht & Athleten-Datenbank")
    st.markdown("## Komplex-Training im Nachwuchs bis Hochleistungssport (Fußball 1 – Komplextraining / Fußball 2 – Speed and Jump)")
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

elif st.session_state.navigations_status == 'Testtabelle':
    if st.session_state.auth_modus != "trainer":
        st.error("Die Testtabelle ist nur für Trainer verfügbar.")
    else:
        render_test_table()

elif st.session_state.navigations_status == 'Operativ':
    col_top1, col_top2 = st.columns([1, 4])
    with col_top1:
        st.button("<< ÜBERSICHT", on_click=navigiere, args=('Uebersicht',))
    with col_top2:
        st.markdown("## Operative Trainingssteuerung")

    st.markdown("<div class='steuermatrix'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #66fcf1 !important; font-size: 26px; font-weight: 900; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 0; margin-bottom: 5px;'>Biometrische Live-Steuerung & Trainingsschwerpunkt</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0aab2; font-size: 14px; margin-bottom: 15px;'>Fokussierte Trainingsansteuerung nach Doc Athletic Train Smart Philosophie</p>", unsafe_allow_html=True)
    
    aktive_sport_schluessel = [k for k in abc_parameter if k.startswith("Fussball_")]
    athlete_actions = st.container()
    jump_area = st.container()
    choices = [json.dumps(identity, ensure_ascii=False) for identity in roster_options(st.session_state.kader_db)]
    choice_labels = {value: roster_label(json.loads(value), st.session_state.kader_db) for value in choices}
    pending = st.session_state.pop("pending_athlete_selection", None)
    if pending and json.dumps(pending, ensure_ascii=False) in choices:
        st.session_state.athlet_gemeinsam = json.dumps(pending, ensure_ascii=False)
    if st.session_state.get("athlet_gemeinsam") not in choices:
        st.session_state.pop("athlet_gemeinsam", None)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        modus = st.selectbox("Steuerungs-Ebene", ["Einzelathlet / Einzelathletin", "Gruppe / Team (Kader)"])
        aktive_kategorie = "Fussball"
        if modus == "Einzelathlet / Einzelathletin":
            if choices:
                selected = st.selectbox("Ziel (Name)", choices,
                    format_func=choice_labels.get, key="athlet_gemeinsam")
                aktive_kategorie, ziel = json.loads(selected)
                aktuelle_daten = st.session_state.kader_db[aktive_kategorie][ziel]
                profil_soll = football_profile(aktuelle_daten["profil"], aktuelle_daten.get("geschlecht", "Männlich"))
            else:
                ziel = "Neuer Athlet"
                aktuelle_daten = {"alter": 10, "groesse": 1.50, "gewicht": 35.0, "profil": "Fussball_U11", "fasertyp": "Schnelligkeit (Sprint)", "reife": "Normalentwickler", "sbe": "SR 2", "t_60": 7.80}
                profil_soll = "Fussball_U11"
        else:
            ziel = st.selectbox("Ziel (Kader / Profil)", aktive_sport_schluessel, key="kader_Fussball")
            profil_soll = ziel
            aktuelle_daten = {"profil": ziel, "alter": profile_age(ziel), "groesse": 1.50 if profile_age(ziel) <= 12 else 1.75, "gewicht": 35.0 if profile_age(ziel) <= 12 else 65.0, "fasertyp": "Schnelligkeit (Sprint)", "reife": "Normalentwickler", "sbe": abc_parameter[ziel]["sbe_ziel"], "t_60": 7.80}
    aktive_athleten_db = st.session_state.kader_db[aktive_kategorie]
    default_focus = aktuelle_daten.get("trainingsschwerpunkt", legacy_focus(aktuelle_daten))
    focus = st.radio("Trainingsschwerpunkt", list(FOCUS_LABELS),
        index=list(FOCUS_LABELS).index(default_focus), format_func=FOCUS_LABELS.get, horizontal=True,
        key=widget_key("focus", aktive_kategorie, modus, ziel))
    speed_mode = focus == "speed_jump"
    focus_saved = focus_settings(aktuelle_daten, focus)
    st.markdown("<div class='badge-fussball'>" + escape(FOCUS_LABELS[focus]) + "</div>", unsafe_allow_html=True)
    st.caption("Ein gemeinsamer Kader für beide Schwerpunkte. Vor dem Wechsel geänderte Vorgaben speichern. Beide Schwerpunkte erlauben eine oder zwei Einheiten pro Woche.")
    shared_fields = {"alter", "geschlecht", "groesse", "gewicht", "fasertyp", "reife", "sbe", "profil", "profilnotizen", "t_60", "t_150", "quelle150", "neu", "velocity", "velocity_note"}
    key_for = lambda field: widget_key(field,
        aktive_kategorie if field in shared_fields or field.startswith(("tempo_ref_", "phase_")) else aktive_kategorie + "_" + focus,
        modus, ziel)

    with c2:
        alter = st.number_input("Alter (Jahre)", min_value=9, max_value=40, value=int(aktuelle_daten["alter"]), key=key_for("alter"), disabled=(st.session_state.auth_modus == "gast" or modus == "Gruppe / Team (Kader)"))
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
    saved_plan = focus_saved.get("planung", {})
    abc_profile = focus_abc_profile(profil_soll, focus)
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
                        for settings in rec.get("fussball_schwerpunkte", {}).values():
                            settings.setdefault("planung", {}).update(startwoche=1, progression=False)
                        rec["aktiver_makrozyklus"] = cycle_name
                    else:
                        restored = deepcopy(archive.pop(chosen_cycle))
                        archive[active_cycle] = saved
                        # Tests gehören zum Athleten, nicht zum Zyklus.
                        restored["sprungtests"] = deepcopy(rec.get("sprungtests", []))
                        restored["feldtests"] = deepcopy(rec.get("feldtests", []))
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
            abc_step = 2.0
            st.caption("Lauf-ABC: +2 m je freigegebener Aufbauwoche, begrenzt auf die Altersstrecke; bei zwei Einheiten kein doppelter Zuwachs.")
            abc_start_m = st.number_input("U11: ABC-Ausgangsstrecke (m)", 10.0, 15.0,
                float(saved_plan.get("abc_start_m", 10.)), .5, key=key_for("abc_start115"), disabled=guest) if band == "U11" else 10.0
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
    org_config = organization_ui(saved_plan.get("organisation", {}), einheiten, key_for("org_"), guest, focus)
    plan_settings = {"steigerung_wdh":rep_step,"abc_step":abc_step,"abc_start_m":abc_start_m,"einheiten":einheiten,"startwoche":startwoche,"rolle":role,"progression":progression,
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
    m_config = m_training_ui(focus_saved.get("m_training", {}), "Fussball", band, key_for("m_training_"), guest)
    speed_total_units = sum(phase_config.get(k, phase_defaults()[k]) for k in ("basis", "jumps", "spruenge")) if phase_config.get("enabled", True) else 14
    speed_config = speed_jump_ui(focus_saved.get("speed_jump", {}), band, geschlecht_wahl, speed_total_units, einheiten, role,
        key_for("speed_jump_"), guest) if speed_mode else focus_saved.get("speed_jump", {})

    hurdle_saved = focus_saved.get("hurdles", {}) if focus_saved.get("hurdles_band", band) == band else {}
    hurdle_config = hurdle_ui(hurdle_saved, band, key_for("hurdles115_"+band), guest) if speed_mode else hurdle_saved

    diag_col1, diag_col2 = st.columns(2)
    with diag_col1:
        t_60 = st.number_input("60m-Referenz (s)", min_value=6.0, max_value=15.0, value=float(aktuelle_daten["t_60"]) if aktuelle_daten.get("t_60") is not None else None, step=0.01, key=key_for("t_60"), disabled=(st.session_state.auth_modus == "gast"))
    with diag_col2:
        auto_150 = round(t_60 * 2.375, 2) if t_60 is not None else None
        quellen = ["berechnet", "gemessen", "ungeklärt"]
        quelle_default = aktuelle_daten.get("t_150_quelle", "ungeklärt" if "t_150" in aktuelle_daten else "berechnet")
        quelle_150 = st.selectbox("Herkunft der 150-m-Zeit", quellen, index=quellen.index(quelle_default),
            key=key_for("quelle150"), disabled=(st.session_state.auth_modus == "gast"))
        if quelle_150 == "berechnet":
            t_150 = auto_150
            st.metric("150-m-Richtwert (berechnet)", f"{t_150:.2f} s" if t_150 is not None else "Noch offen")
        else:
            t_150 = st.number_input("150m-Referenz (s)", min_value=0.01, max_value=120.0,
                value=float(aktuelle_daten.get("t_150", auto_150)) if aktuelle_daten.get("t_150", auto_150) is not None else None, step=0.01,
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

    neuer_name = ""

    def profile_for_save(create_new=False):
        if neuer_name and not create_new:
            raise ValueError("Bitte zuerst das neue Athletenprofil oben anlegen und speichern. Plan und Tests können danach dieser Person zugeordnet werden.")
        save_sport = "Fussball" if create_new else aktive_kategorie
        record = deepcopy(aktuelle_daten)
        settings_by_focus = {key: focus_settings(aktuelle_daten, key) for key in FOCUS_LABELS}
        if create_new:
            settings_by_focus = {}
            record.pop("fussball_schwerpunkte", None)
            record.pop("sprungtests", None)
            record.pop("feldtests", None)
            record.pop("makrozyklen", None)
            record.pop("aktiver_makrozyklus", None)
            record.pop("einheitenprotokoll", None)
        record.update({"alter": int(alter), "groesse": float(groesse), "gewicht": float(gewicht), "profil": storage_profile(profil_soll, save_sport),
            "phasensteuerung":({**phase_config,"references":{},"jumps_ready":False,"spruenge_ready":False} if create_new and ziel in aktive_athleten_db else phase_config), "lastreferenz":({} if create_new and ziel in aktive_athleten_db else load_reference), "geschlecht": geschlecht_wahl, "fasertyp": ft, "reife": reife, "sbe": sbe_ziel, "notizen": profile_notes,
            "m_training": (m_training_defaults(save_sport, band) if create_new or save_sport != "Fussball" else m_config),
            "t_60": float(t_60) if t_60 is not None else None, "t_150": float(t_150) if t_150 is not None else None, "t_150_quelle": quelle_150, "planung":plan_settings, "tempo_referenzen":tempo_references})
        settings_by_focus[focus] = {"planung": deepcopy(plan_settings),
            "m_training": m_training_defaults("Fussball", band) if create_new and ziel in aktive_athleten_db else deepcopy(m_config),
            "speed_jump": deepcopy(speed_config), "hurdles": deepcopy(hurdle_config), "hurdles_band": band}
        # An age-group change resets only age-specific M-sprint settings.
        for settings in settings_by_focus.values():
            if settings.get("hurdles_band", band) != band:
                settings["hurdles"] = {}
                settings["hurdles_band"] = band
            if settings.get("speed_jump"):
                settings["speed_jump"] = normalize_speed_jump(settings["speed_jump"], band, geschlecht_wahl)
            if settings.get("m_training", {}).get("band", band) != band:
                settings["m_training"] = m_training_defaults("Fussball", band)
        if record.get("t_150") is None:
            record.pop("t_150", None)
        record["fussball_schwerpunkte"] = settings_by_focus
        record["trainingsschwerpunkt"] = focus
        return record

    if modus == "Einzelathlet / Einzelathletin" and st.session_state.auth_modus == "trainer":
        with athlete_actions:
            st.subheader("Athletin / Athlet anlegen und speichern")
            neuer_name = st.text_input("Neuen Athleten-Namen eingeben (zum Anlegen):", value="", key=key_for("neu")).strip()
            speichern = st.button("Athletenprofil und Schwerpunkt speichern", type="primary")
            st.caption("Neues Profil: Namen eingeben, unten die Werte anpassen und hier speichern. Bestehendes Profil: Namensfeld leer lassen. Vor dem Athletenwechsel speichern.")
        if speichern:
            ziel_name = neuer_name if neuer_name else ziel
            try:
                if not aktive_athleten_db and not neuer_name:
                    raise ValueError("Bitte zuerst einen Athletennamen eingeben.")
                if neuer_name and any(neuer_name in athletes for athletes in st.session_state.kader_db.values()):
                    raise ValueError("Dieser Name ist bereits vorhanden. Bitte das vorhandene Profil auswählen.")
                updated = deepcopy(st.session_state.kader_db)
                save_sport = "Fussball" if neuer_name else aktive_kategorie
                record = profile_for_save(create_new=bool(neuer_name))
                updated[save_sport][ziel_name] = record
                revision = speichere_kader_in_datei(updated, st.session_state.kader_revision)
                st.session_state.kader_db = updated
                st.session_state.kader_revision = revision
                st.session_state.pending_athlete_selection = (save_sport, ziel_name)
                st.session_state.edit_epoch = st.session_state.get("edit_epoch", 0) + 1
                st.session_state.save_notice = f"Profil {ziel_name} gespeichert und zur Bearbeitung ausgewählt."
                st.rerun()
            except (OSError, sqlite3.Error, StorageError, ValueError, StorageConflict) as exc:
                athlete_actions.error(f"Nicht gespeichert: {exc}")

    with jump_area:
        render_field_history(aktuelle_daten)
        if modus == "Einzelathlet / Einzelathletin":
            render_individual_shuttle(aktuelle_daten, aktive_kategorie, ziel, profile_for_save, guest)
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
                        row["Erfassung"] = "Protokollwert; Einzelversuche nicht angegeben" if "protokollwerte" in test else "Einzelversuche"
                        for field, label in JUMP_TESTS.items():
                            for i, value in enumerate(test.get(field, [None, None, None]), 1):
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
                    st.caption("Dieser Knopf speichert den neuen Test zusammen mit den aktuellen Profilwerten und Schwerpunktvorgaben. Frühere Tests bleiben erhalten.")
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
                            updated[aktive_kategorie][ziel] = profile_for_save()
                            updated[aktive_kategorie][ziel].setdefault("sprungtests", []).append(new_test)
                            revision = speichere_kader_in_datei(updated, st.session_state.kader_revision)
                            st.session_state.kader_db = updated
                            st.session_state.kader_revision = revision
                            st.session_state[jump_epoch_key] = jump_epoch + 1
                            st.session_state.save_notice = f"Sprungtest und aktuelle Profilwerte für {ziel} gespeichert."
                            st.rerun()
                        except (OSError, sqlite3.Error, StorageError, ValueError, StorageConflict) as exc:
                            st.error(f"Test nicht gespeichert: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

    reife_intern = "Spätentwickler" if "Spät" in reife else "Frühentwickler" if "Früh" in reife else "Normalentwickler"

    if t_60 is None or t_150 is None:
        st.info("Profil und Tests können gespeichert werden. Für berechnete Laufzeiten und die vollständige Trainingsausgabe bitte die fehlende Sprintreferenz oben ergänzen. Es wird keine Ersatzzeit eingesetzt.")
        st.stop()

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
    st.subheader(f"{FOCUS_LABELS[focus]}: {ziel}")

    vorgaben = abc_parameter.get(abc_profile, {"sets": 4, "start_m": 15.0, "step_m": 2.5})
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
        tief_kh = "ohne Kurzhanteln"
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
        if band == "U11":
            strength_exercise = "Kreuzhebesprünge auf der Stelle"
            hex_text = "2 kg je Kurzhantel"
            bag_exercise = "Front Squat Jumps"
            bag_text = "2 kg je Kurzhantel"
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
        abc_dist, abc_load = abc_values(band, geschlecht_wahl, week, progression, abc_start_m)
        warmup = warmup_text(band, te_num)
        bag_count = weekly_reps(bag_start, week, 20 if capacity else 15, progression, rep_step)
        quality_day = short_day or speed_mode
        bag_wdh = "8–6–5 Wdh. (3 Sätze)" if quality_day else f"{bag_count} Wdh. je Satz"
        day_label = "Vollständige Komplexeinheit · 1 TE/Woche" if einheiten == 1 else ("Neuromuskulär / vor dem Spiel" if short_day else "Haupttag")
        split_main = einheiten == 2 and not short_day
        main_sets = str(org_config.get("main_sets", 4)) if split_main else "3"
        current_unit = "Basis" if einheiten == 1 else "TE2" if short_day else "TE1"
        timing = weekly_timing("Fussball", band, einheiten, current_unit)
        extra_rows = ""
        m_sprint_row = ""
        m_rows = m_training_rows(m_config, "Fussball", band, te_num, einheiten, short_day)
        hurdle_m = speed_mode and hurdle_plan(hurdle_config, band, te_num)["form"] == HURDLE_FORMS[0]
        if hurdle_m:
            m_rows = [row for row in m_rows if row["Block"] != "M-Sprint ohne Ball"]
        for m_row in m_rows:
            cells = [m_row["Block"], m_row["Trainingsmittel"], m_row["Sätze"],
                     m_row["Wdh_oder_Strecke"], m_row["Zusatzlast"],
                     m_row["Intensität"] + "; " + m_row["Fokus"], m_row["Pause"]]
            m_sprint_row += '<tr style="background:#e8f4f0">' + ''.join(
                '<td style="padding:6px;border:1px solid #aaa">'+escape(cell)+'</td>' for cell in cells) + '</tr>'

        if quality_day:
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


        abc_last_str = "Ohne Stange" if abc_load == "0" else f"Stange {abc_load} kg gesamt; über Kopf auch beim beschleunigten Rückweg"
        row_abc = rows_html(abc_rows_115(band, geschlecht_wahl, week, progression, abc_start_m))

        pause_komplex = PARTNER_PAUSE

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
        if speed_mode:
            runs = speed_config["short_runs"] if short_day else speed_config["runs"]
            tl_pos = "nach_komplex"
            tl_text = f'{runs} × {speed_config["distance_m"]} m Beschleunigung ohne Ball'
            tl_pause = PARTNER_PAUSE
            if hurdle_m or any(row["Block"] == "M-Sprint ohne Ball" for row in m_rows):
                tl_text = "M-Sprints gemäß eigenem Block; keine zusätzlichen geraden Beschleunigungen"
            day_label = FOCUS_LABELS[focus] + " · " + ("kürzere zweite Einheit" if short_day else "Schwerpunkteinheit")
        test_note = (f"Testauswertung (keine Laufvorgabe): {test_distance} m: {test_seconds / (test_percent / 100):.1f} s bei {test_percent}% der gemessenen Testgeschwindigkeit"
                     if test_seconds > 0 else "Tempolauf-Zielzeit: Test derselben Distanz noch eingeben")
        phase_label = "Phase 1: Komplextraining: Kraft und anschließende Sprünge/Sprints" if woche <= 7 else "Phase 2: Laktazide Vorab-Ermüdung" if woche <= 11 else "Phase 3: Marathon & Zuspitzung"
        
        if short_day:
            phase_label = "Neuromuskulärer Erinnerungsreiz"
        row_gla_vorab = ""
        if tl_pos == "vor_komplex":
            row_gla_vorab = f'<tr style="background-color: #FCE4D6;"><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold; color: #C00000;">Block 1: GLA Vorab</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{tl_text}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">Serie</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Kaskade vor Kraft</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">60-70% Vmax</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{tl_pause}</td></tr>'

        row_tl_transfer = ""
        row_speed_tempo = ""
        if tl_pos in ["nach_komplex", "marathon"]:
            row_tl_transfer = f'<tr style="background-color: #FCE4D6;"><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Block 2: Lauf / Transfer</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{tl_text}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Variabel</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Direct-Transfer</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{escape("Kurz und hochwertig; vollständige Erholung" if quality_day else "Individuelles Trainingsziel")}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{tl_pause}</td></tr>'

        if speed_mode and not short_day and band not in ("U11", "U13"):
            block_rounds, short_distances = speed_block_one(speed_config, speed_build_index(te_num, einheiten, role), band, geschlecht_wahl)
            has_m_sprints = hurdle_m or any(row["Block"] == "M-Sprint ohne Ball" for row in m_rows)
            if has_m_sprints:
                row_tl_transfer = ""
            else:
                short_sequence = " + ".join(f"{distance} m" for distance in short_distances)
                short_total = block_rounds * sum(short_distances)
                cells = ["Speed Block 1: Lauf / Transfer", "Sprintschnelligkeitsausdauer: " + short_sequence,
                         f"{block_rounds} Durchgänge", f"{len(short_distances)} Läufe je Durchgang; {block_rounds*len(short_distances)} Läufe / {short_total} m insgesamt",
                         "ohne Zusatzlast", "Gegeneinander bei sauberer Lauftechnik; fußballspezifische Sprintschnelligkeitsausdauer",
                         "Nach jedem Lauf gleich lange Gehstrecke (" + " / ".join(map(str, short_distances)) + " m); Lohnende Pause durch Partnerwechsel"]
                row_tl_transfer = '<tr style="background:#fce4d6">' + ''.join('<td>'+escape(value)+'</td>' for value in cells) + '</tr>'
            tempo_distances = speed_tempo_distances(speed_config, band, geschlecht_wahl, te_num, speed_total_units, short_day, einheiten, role)
            if tempo_distances:
                tempo_sequence = " + ".join(f"{distance} m" for distance in tempo_distances[:2])
                cells = ["Speed Block 2: Lauf / Transfer", "Tempolauf-Paar: " + tempo_sequence,
                         "3 Durchgänge", f"2 Läufe je Durchgang; 6 Läufe / {sum(tempo_distances)} m insgesamt", "ohne Zusatzlast",
                         f'{speed_config["tempo_percent"]}% der jeweiligen Streckenreferenz; längster Lauf {max(tempo_distances)} m',
                         "Nach jedem Lauf 100 m Gehpause; Lohnende Pause durch Partnerwechsel"]
                row_speed_tempo = '<tr style="background:#fce4d6">' + ''.join('<td>'+escape(value)+'</td>' for value in cells) + '</tr>'

        if effective_phase in ("Grundlast", "Jumps", "Sprünge"):
            phase_label = f"{effective_phase} · vorgesehene Phase: {planned_phase}"
        if speed_mode and effective_phase == "Bestehender Plan":
            phase_label = "Speed and Jump · " + hurdle_plan(hurdle_config, band, te_num)["form"]
        strength_intensity = "Technisch kontrolliert" if effective_phase == "Grundlast" else "Explosiv bei sauberer Technik"
        row_hurdles = rows_html(hurdle_rows_115(hurdle_config, band, te_num)) if speed_mode else f'''<tr style="background-color: #BDD7EE;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Komplex: Hürden</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Hürden-Tiefsprünge (Reaktiv / DVZ)</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"6–8 Hürden" if quality_day else "8–12 Hürden (Trainerbasis)"} ({tief_hoehe})</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{tief_kh}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Maximal explosiv</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{PARTNER_PAUSE}</td>
</tr>
'''
        html_matrix = f'''<meta charset="utf-8">
<div class="druck-block" style="background-color: #111111; color: #ffffff; border: 2px solid #45a29e; border-radius: 8px; padding: 20px; margin-top: 20px; font-family: Arial, sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #66fcf1; padding-bottom: 5px;">
<h3 style="margin: 0; color: #66fcf1 !important;">TRAININGSMATRIX - EINHEIT: TE {woche}</h3>
<span style="color: #ffb703; font-weight: bold; font-size: 14px;">{phase_label}</span>
</div>
<p style="color: #ffffff !important; font-size: 14px; margin-top: 8px;"><strong>Schwerpunkt:</strong> {escape(FOCUS_LABELS[focus])} | <strong>Makrozyklus:</strong> {escape(aktuelle_daten.get("aktiver_makrozyklus", "Bestand"))} | <strong>Athlet:</strong> {escape(ziel)} ({gewicht} kg) | <strong>Woche:</strong> {week}, Einheit {day} | <strong>Ziel:</strong> {day_label} | <strong>Phase:</strong> {effective_phase} (vorgesehen: {planned_phase}) | <strong>Lauf-ABC Last:</strong> {abc_last_str}</p>
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
{row_abc}
{row_gla_vorab}
{row_hurdles}
<tr style="background-color: #FCE4D6;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Eigenständige Kraft-Hauptübung</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{strength_exercise}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{"3" if quality_day else "3–4 (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"8–6–5 Wdh." if quality_day else "8–12 Wdh. (Trainerbasis)"}</td>
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
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"5–8 Wdh." if quality_day else "12–15 Wdh. (Trainerbasis)"}</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Griffball {gb_last_kg} kg</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Max. Schnellkraft</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">60s</td>
</tr>
{extra_rows}
{m_sprint_row}
{row_tl_transfer}
{row_speed_tempo}
<tr style="background-color: #E2EFDA;">
<td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">Block 3: Rumpf/TRX</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Zug im Schrägliegehang am TRX / Barren</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">3</td>
<td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"5–8 Wdh." if quality_day else "12–15 Wdh. (Trainerbasis)"}</td>
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
        html_matrix = organize_multisport_html(html_matrix, einheiten, short_day, main_sets, "Fussball", band, org_config, timing, focus, speed_block_one(speed_config, speed_build_index(te_num, einheiten, role), band, geschlecht_wahl)[0] if speed_mode else None)
        rendered_plans[te_num] = html_matrix
        html_matrices += html_matrix

    if modus == "Einzelathlet / Einzelathletin" and ziel in aktive_athleten_db:
        protocol_te = st.selectbox("Einheit für Soll-/Ist-Protokoll", list(te_liste), key=key_for("protocol_te"))
        unit_workflow(aktuelle_daten, aktive_kategorie, ziel, protocol_te, plan_as_text(rendered_plans[protocol_te]), key_for, guest, weekly_timing("Fussball", band, einheiten, "TE2" if unit_context(protocol_te, einheiten, startwoche, role)[2] else "TE1"), focus=focus, profile_for_save=profile_for_save)
    st.markdown(html_matrices, unsafe_allow_html=True)
    st.markdown("---")

    st.download_button(
        label="💾 Trainingsplan und Tempotabelle herunterladen",
        data="<!doctype html><html lang=\"de\"><head><meta charset=\"utf-8\"><title>Doc Athletic Train Smart Evolution Software – Trainingsplan</title><style>body{font-family:Arial,sans-serif}table{border-collapse:collapse}th,td{padding:6px;border:1px solid #aaa}@media print{@page{size:A4 landscape;margin:10mm}.druck-block{break-before:page;background:#fff!important;color:#111!important;border:0!important}.druck-block h3,.druck-block p,.druck-block span{color:#111!important}}</style></head><body>" + "<h1>Doc Athletic Train Smart Evolution Software 115 · Trainingsentwurf</h1><p>Trainerplanung nach individuellen Referenzen und Belastungsverträglichkeit. Berechnete Richtwerte sind Orientierungshilfen.</p><h2>Tempotabelle 50–800 m</h2><p>Prozentwerte der mittleren Referenzgeschwindigkeit. Zwischenwerte und ausdrücklich aktivierte Fortsetzungen sind als Richtwerte gekennzeichnet. Einlaufzeiten bleiben separat.</p>" + pd.DataFrame(tempo_data).to_html(index=False, escape=True) + html_matrices + "</body></html>",
        file_name=f"Doc_Athletic_115_{focus}_{ziel.replace(' ', '_')}.html",
        mime="text/html; charset=utf-8"
    )

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        st.markdown("""<div style="text-align: center; border: 2px solid #45a29e; border-radius: 8px; padding: 15px; background-color: #111111;">
<h2 style="color: #66fcf1 !important; margin-bottom: 5px; font-family: Arial, sans-serif;">Aufgeben gilt nicht!</h2>
<p style="color: #ffb703 !important; font-size: 16px; font-weight: bold; margin: 8px 0;">>>Das, was du fühlst, ist nicht das, was du kannst.<<</p>
<p style="color: #ffffff !important; font-size: 13px; letter-spacing: 1px; margin-top: 5px;">DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE 115</p>
</div>""", unsafe_allow_html=True)
        lade_bild(["Foto.jpg", "Foto.JPG", "foto.jpg", "foto.JPG", "Foto.jpeg", "foto.jpeg", "Foto.png", "foto.png"], use_col=True)
