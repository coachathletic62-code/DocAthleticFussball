# ============================================================================
# DOC ATHLETIC TRAIN SMART EVOLUTION SOFTWARE - FUSSBALL (Version 120)
# ChatGPT überarbeitet auf Grundlage 23.8.5; Modul 1
# Überarbeitet: kurze Trainingsansicht, Athletenprofile, Tests, Einheitenverlauf
# Stand: 24.09.2026 – Entwicklungsstatus, Trainingsmatrix und Trainer-Veto
# ============================================================================
import streamlit as st
from doc_athletic_input import voice_number_input
from doc_athletic_core import (PARTNER_PAUSE, abc_rows_115, build_tempo_table, phase_defaults, phase_validate, phase_status, phase_exercise_label, weekly_reps, unit_context, kreuzheben_load, cheer_load, profile_age, age_matches_profile, powerbag_load)
from doc_athletic_storage import (StorageConfig, StorageConflict, StorageError, load_state, save_state, export_backup, decode_backup)
from doc_athletic_core import AGE_BANDS, ASSIGNMENT_RULE, calendar_band, training_assignment, validate_assignment
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
import csv
import io
import re
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile
SAVED_PLAN_STYLE = """
.doc-saved-plan {background:#111;color:#f5f5f5;border:2px solid #45a29e;border-radius:8px;padding:20px;line-height:1.5}
.doc-saved-plan p,.doc-saved-plan h3 {color:#f5f5f5 !important}
.doc-saved-plan p {white-space:pre-wrap;overflow-wrap:anywhere;margin:0 0 .5rem}
.doc-saved-plan h3 {margin:0 0 1rem;color:#66fcf1 !important}
.doc-saved-plan .plan-table {overflow-x:auto;margin:1rem 0}
.doc-saved-plan table {width:100%;border-collapse:collapse;font-size:.9rem}
.doc-saved-plan th,.doc-saved-plan td {padding:8px;border:1px solid #aaa;text-align:left;vertical-align:top;white-space:pre-wrap}
.doc-saved-plan th {background:#1f4e78;color:#fff !important}
.doc-saved-plan td {background:#f2f5f7;color:#111 !important}
.doc-saved-plan tr:nth-child(even) td {background:#fff}
@media print {.doc-saved-plan {background:#fff;color:#111;border:0;padding:0}.doc-saved-plan p,.doc-saved-plan h3 {color:#111 !important}}
"""
st.set_page_config(page_title="Doc Athletic – Fußball · 120", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>"+SAVED_PLAN_STYLE+"""
.stApp {background:#0b0c10;color:#f5f5f5;color-scheme:dark}
[data-testid="stHeader"] {background:#0b0c10;color:#f5f5f5}
[data-testid="stHeader"] button,[data-testid="stHeader"] svg {color:#f5f5f5 !important}
[data-testid="stMainBlockContainer"] {padding-top:4rem;padding-bottom:2rem}
h1,h2,h3,h4,h5,h6,p,label {color:#f5f5f5 !important}
h1 {font-size:clamp(1.5rem,3vw,2.1rem) !important}
h2 {font-size:1.4rem !important;color:#66fcf1 !important}
[data-testid="stCaptionContainer"] p {color:#c5c6c7 !important}
[data-testid="stTooltipContent"],[data-testid="stTooltipErrorContent"] {
    background:#fff !important;color:#111 !important;border:1px solid #767676;
}
[data-testid="stTooltipContent"] *,[data-testid="stTooltipErrorContent"] * {
    color:#111 !important;-webkit-text-fill-color:#111 !important;
}
[data-testid="stAlertContainer"] {background:#f1f5f9 !important;color:#111 !important;}
[data-testid="stAlertContainer"] * {color:#111 !important;-webkit-text-fill-color:#111 !important;}
[data-testid="stWidgetLabel"] p,[data-testid="stRadio"] label p {color:#f5f5f5 !important}
[data-testid="stText"],[data-testid="stText"] * {color:#f5f5f5 !important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background:#fff !important;color:#111 !important;-webkit-text-fill-color:#111 !important;
    caret-color:#111 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] [role="option"] * {color:#111 !important;-webkit-text-fill-color:#111 !important}
[data-baseweb="popover"] [role="listbox"] {background:#fff !important}
[data-testid="stTextInput"] input:disabled,[data-testid="stTextArea"] textarea:disabled {
    background:#dce2e7 !important;opacity:1;
}
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button {
    background:#1f2833 !important;border:2px solid #45a29e !important;border-radius:8px;width:100%;
}
[data-testid="stButton"] button *,[data-testid="stFormSubmitButton"] button * {color:#f5f5f5 !important}
[data-testid="stButton"] button:focus-visible,[data-testid="stFormSubmitButton"] button:focus-visible {
    outline:3px solid #66fcf1 !important;
}
[data-testid="stDownloadButton"] button {background:#66fcf1 !important;border:2px solid #45a29e !important;width:100%}
[data-testid="stDownloadButton"] button * {color:#111 !important;font-weight:700}
[data-testid="stRadio"] label {background:#1f2833;border:1px solid #45a29e;border-radius:8px;padding:8px 14px}
[data-testid="stExpander"] details > summary {background:#17191c !important;color:#fff !important}
[data-testid="stExpander"] details > summary * {color:#fff !important}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#45a29e !important}
table {border-collapse:collapse} td,th {padding:6px;border:1px solid #aaa}
@media print {
    [data-testid="stSidebar"],.stButton,.stDownloadButton {display:none}
    .st-key-trainer_instructions {display:none !important}
    .druck-block {background:#fff !important;color:#111 !important;border:0 !important}
    .druck-block h3,.druck-block p,.druck-block span {color:#111 !important}
}
</style>""",unsafe_allow_html=True)
def lade_bild(dateinamen_liste, use_col=False):
    for name in dateinamen_liste:
        if os.path.exists(name):
            if use_col:
                st.image(name, width="stretch")
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
BUILD_STAND = '25.09.2026 · Stufe 1: 16 Einheiten, Kraftphasen Stand–Jumps–Sprünge, Tempolauf-Pyramiden, Retest, Empfehlungen für den Folgezyklus'
PROFILE_DEFAULTS = {'Fussball_U11': {'sbe_ziel': 'SR 3'}, 'Fussball_U13': {'sbe_ziel': 'SR 2-3'}, 'Fussball_U15_m': {'sbe_ziel': 'SR 2'}, 'Fussball_U15_w': {'sbe_ziel': 'SR 2'}, 'Fussball_U17_m': {'sbe_ziel': 'SR 1-2'}, 'Fussball_U17_w': {'sbe_ziel': 'SR 1-2'}, 'Fussball_U20_m': {'sbe_ziel': 'SR 1'}, 'Fussball_U20_w': {'sbe_ziel': 'SR 1'}, 'Fussball_U23_m': {'sbe_ziel': 'SR 1-0'}, 'Fussball_U23_w': {'sbe_ziel': 'SR 1-0'}, 'Fussball_MASTER_m': {'sbe_ziel': 'SR 0'}, 'Fussball_MASTER_w': {'sbe_ziel': 'SR 0'}, 'Leichtathletik_U11': {'sbe_ziel': 'SR 3'}, 'Leichtathletik_U13': {'sbe_ziel': 'SR 2-3'}, 'Leichtathletik_U15': {'sbe_ziel': 'SR 2'}, 'Leichtathletik_U17_m': {'sbe_ziel': 'SR 1-2'}, 'Leichtathletik_U17_w': {'sbe_ziel': 'SR 1-2'}, 'Leichtathletik_U20_m': {'sbe_ziel': 'SR 1'}, 'Leichtathletik_U20_w': {'sbe_ziel': 'SR 1'}, 'Leichtathletik_U23_m': {'sbe_ziel': 'SR 0'}, 'Leichtathletik_U23_w': {'sbe_ziel': 'SR 0'}, 'Leichtathletik_MASTER_m': {'sbe_ziel': 'SR 0'}, 'Leichtathletik_MASTER_w': {'sbe_ziel': 'SR 0'}}
# Version 115: agreed working values; saved plans remain immutable until edited.
PARTNER_ORGANIZATION = (
    "Staffelbetrieb mit mehreren Linien bzw. Übungsreihen, bei Gewichtsstangen "
    "mindestens zwei bis drei Linien; die Partner wechseln nach jeder Ausführung."
)
HURDLE_FORMS = ("M-Hürdensprints", "Hürden-Steigesprünge", "Hürden-Tiefsprünge / CMJ", "Ohne Hürden")
M_HURDLE_EDGES = {"U11": (12., 15.), "U13": (15., 18.), "U15": (15., 20.),
                  "U17": (17., 20.), "U20": (20., 25.), "U23": (20., 28.), "MASTER": (20., 28.)}
M_HURDLE_HEIGHTS = {"U11": 25, "U13": 30, "U15": 38, "U17": 45, "U20": 45, "U23": 45, "MASTER": 45}
U11_DUMBBELLS = {"Cheerleading": 1, "Umsatz-/Ausstoßsprünge auf der Stelle": 1,
                 "Squat-/Stoßsprünge": 1, "Candle Jumps": 1, "Burpees mit Kurzhanteln": 1,
                 "Burpees ohne Kurzhanteln": 0, "Kreuzhebesprünge auf der Stelle": 2,
                 "Front Squat Jumps": 2}
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

def apply_training_assignment(record, calendar, development, gender, veto_band=None, veto_note=""):
    """Bereitet neue Vorgaben vor; gespeicherte Einheiten und Messungen bleiben erhalten."""
    result = training_assignment(calendar, development, veto_band)
    updated = deepcopy(record)
    band = result["effective"]
    sport = record.get("profil", "Fussball_U11").split("_")[0]
    previous_band = record.get("profil", "").split("_")[1:2]
    previous_gender = record.get("geschlecht", "Weiblich" if record.get("profil", "").endswith("_w") else "Männlich")
    changed = previous_band != [band] or previous_gender != gender
    updated.update(kalenderklasse=calendar, reife=development, geschlecht=gender,
                   profil=storage_profile(football_profile("Fussball_"+band, gender),sport),
                   trainingszuordnung={"regel":ASSIGNMENT_RULE,"veto_klasse":veto_band,"veto_notiz":veto_note if veto_band else ""})
    if changed:
        # Retain schedule and measured test references, never an older class's load overrides.
        retained = {"einheiten","startwoche","rolle","test_distanz","test_zeit",
                    "tempo_interpolation","tempo_extrapolation","organisation","zyklus_einheiten"}
        def reset_plan(plan):
            reset = {**{k:deepcopy(v) for k,v in plan.items() if k in retained},"progression":True}
            if 'organisation' in reset:
                reset['organisation'].pop('main_sets',None)
            return reset
        # Preserve measured M-run references with their original distance context.
        # They must never be interpreted as times for a newly assigned course.
        references = deepcopy(record.get('m_lauf_referenzen',[]))
        configs = [record.get('m_training',{})] + [cfg.get('m_training',{}) for cfg in record.get('fussball_schwerpunkte',{}).values()]
        for config in configs:
            for kind in ('ball','maximal'):
                part = config.get(kind,{})
                if part.get('run_seconds') is not None:
                    measurement = {'klasse':config.get('band',previous_band[0]),'form':kind,
                                   'edge_m':part.get('edge_m'), 'timed_distance_m':part.get('timed_distance_m'),
                                   'run_seconds':part['run_seconds'],'notes':part.get('notes','')}
                    if measurement not in references:
                        references.append(measurement)
        if references:
            updated['m_lauf_referenzen'] = references
        updated["planung"] = reset_plan(record.get("planung",{}))
        updated["m_training"] = m_training_defaults(sport,band)
        for cfg in updated.get("fussball_schwerpunkte",{}).values():
            cfg.update(planung=reset_plan(cfg.get("planung",{})),
                       m_training=m_training_defaults("Fussball",band),
                       speed_jump=speed_jump_defaults(band,gender),hurdles={},hurdles_band=band)
        phases = phase_defaults()
        phases['references'] = deepcopy(record.get('phasensteuerung',{}).get('references',{}))
        for ref in phases.get("references",{}).values():
            ref.update(apply=False,chosen=0)
        updated["phasensteuerung"] = phases
        updated["sbe"] = PROFILE_DEFAULTS[football_profile(updated["profil"],gender)]["sbe_ziel"]
    return updated, result, changed

# Frank Müller, 25.09.2026: 14 Einheiten je Halbjahr; bei 15/16 Einheiten werden
# nach TE 11 Steigerungseinheiten eingeschoben. Shuttle, Marathon und Abschlusstest
# folgen immer als letzte drei Einheiten.
CYCLE_UNIT_CHOICES = (14, 15, 16)
PHASE_NAMES = {"Grundlast": "Stand", "Jumps": "Jumps", "Sprünge": "Sprünge"}
def cycle_units(record, focus):
    units = focus_settings(record, focus).get("planung", {}).get("zyklus_einheiten", 16)
    return units if units in CYCLE_UNIT_CHOICES else 16
def cycle_plan(record, focus, band):
    """Phasen passend zur Einheitenzahl; die letzte Einheit ist der Retest."""
    units = cycle_units(record, focus)
    cfg = phase_defaults()
    cfg.update(record.get("phasensteuerung", {}))
    if cfg["enabled"]:
        gap = units - (cfg["basis"] + cfg["jumps"] + cfg["spruenge"])
        if gap > 0 and cfg["spruenge"] + gap <= 14:
            cfg["spruenge"] += gap
        while gap < 0 and cfg["spruenge"] > 1:
            cfg["spruenge"] -= 1; gap += 1
        while gap < 0 and cfg["jumps"] > 1:
            cfg["jumps"] -= 1; gap += 1
        total = max(units, cfg["basis"] + cfg["jumps"] + cfg["spruenge"])
    else:
        total = units
    return cfg, total, units
# Frank Müller, 25.09.2026: Wiederholungen Jungs 8 → +1 → 15, Mädchen 10 → +1 → 20.
def rep_rule(gender, level):
    start, cap = (10, 20) if gender == "Weiblich" else (8, 15)
    reps = start + max(0, level - 1)
    if reps <= cap:
        return f"{reps} Wdh."
    return f"{cap} Wdh. · Obergrenze erreicht: nächste Laststufe nach Tonnage-Regel (Trainer)"
# Tempolauf-Pyramiden: Start in TE 1, dann +50 m je Einheit (U13: +25 m) bis zur Obergrenze.
TEMPO_START = {("U13", "Männlich"): [100, 100, 50], ("U13", "Weiblich"): [100, 100, 50],
               ("U15", "Männlich"): [250, 200, 150], ("U15", "Weiblich"): [250, 200, 150],
               ("U17", "Männlich"): [500, 300, 200], ("U17", "Weiblich"): [250, 200, 150],
               ("U20", "Männlich"): [500, 300, 200], ("U20", "Weiblich"): [500, 400, 300],
               ("U23", "Männlich"): [600, 400, 300], ("U23", "Weiblich"): [500, 400, 300],
               ("MASTER", "Männlich"): [600, 400, 300], ("MASTER", "Weiblich"): [500, 400, 300]}
TEMPO_CAP = {("U13", "Männlich"): 150, ("U13", "Weiblich"): 150, ("U15", "Männlich"): 600, ("U15", "Weiblich"): 600,
             ("U17", "Männlich"): 700, ("U17", "Weiblich"): 600, ("U20", "Männlich"): 800, ("U20", "Weiblich"): 600,
             ("U23", "Männlich"): 800, ("U23", "Weiblich"): 800, ("MASTER", "Männlich"): 800, ("MASTER", "Weiblich"): 800}
def tempo_pyramid(band, gender, level):
    """Zuerst den letzten Lauf an den vorherigen angleichen, dann den davor;
    sind alle gleich, den ersten Lauf verlängern. Nie über die Obergrenze."""
    runs = list(TEMPO_START[(band, gender)])
    cap = TEMPO_CAP[(band, gender)]
    step = 25 if band == "U13" else 50
    for _ in range(max(0, level - 1)):
        for j in range(len(runs) - 1, 0, -1):
            if runs[j] < runs[j - 1]:
                runs[j] = min(runs[j] + step, runs[j - 1])
                break
        else:
            if runs[0] + step <= cap:
                runs[0] += step
    return runs
def tempo_intensity(distance, band=None):
    if band == "U13":
        return "60–70 %"  # TM-Liste D1: Tempoläufe bis 150 m bei 60–70 %
    return "60 %" if distance >= 500 else "70 %" if distance >= 250 else "80 %"
def u11_endurance(level):
    """E2-Praxis 2025: alaktazid, Grundlagenausdauer locker im Team-Style."""
    if level <= 4: return "1 × 400 m"
    if level <= 7: return "2 × 400 m"
    if level == 8: return "2 × 550 m"
    return "2 × 600 m (Richtwert 2:28–3:05 min)"
def retest_html(band, gender, bag_text, gb_last_kg, name, cycle):
    distances = {"U11": ("20 m", "40 m", None), "U13": ("30 m", "60 m", "150 m")}.get(band, ("60 m", "250 m", "600 m"))
    ball = f"Griffball {gb_last_kg} kg"
    squat = "5× Front Squat Jumps" if band == "U11" else "5× Squat-Sprünge"
    ums = "5× Umsatz/Ausstoß-Jumps" if band == "U11" else "5× Umsatz/Ausstoß-Sprünge"
    rows = [["Retest Block 1", squat, "1", distances[0] + " Sprint auf Zeit", bag_text, "Maximal", "Volle Erholung"],
            ["Retest Block 2", ums, "1", distances[1] + " auf Zeit", ball, "Maximal", "Volle Erholung"]]
    if distances[2]:
        rows.append(["Retest Block 3", "5× seitl. Pendel-Shuttle über Hürde", "1", distances[2] + " auf Zeit", "Hürde", "Maximal", "Volle Erholung"])
    else:
        rows.append(["Retest Block 3", "5er-Hop links / rechts, 5er-Schlusssprung", "je 1", "Weite in m", "ohne", "Maximal", "Volle Erholung"])
    body = "".join("<tr>" + "".join("<td>" + escape(c) + "</td>" for c in r) + "</tr>" for r in rows)
    head = "".join("<th>" + h + "</th>" for h in ["Block / Phase", "Trainingsmittel / Übung", "Sätze", "Wdh. / Distanz", "Hardware / Zusatzlast", "Intensität", "Pause"])
    return ('<div class="druck-block doc-saved-plan"><h3>TRAININGSMATRIX - EINHEIT: RETEST</h3>'
            f'<p>Standard-Retest am Zyklusende · Makrozyklus: {escape(cycle)} · Athlet: {escape(name)}</p>'
            '<p>Erwärmung 800 m einlaufen, Lauf-ABC. Jeweils Kraftteil direkt vor dem Lauf auf Zeit. Zeiten unter „Durchführung notieren“ eintragen; sie dienen dem Jahresvergleich. Per Trainer-Veto kann der Retest anders gestaltet werden (z. B. Komplex-Shuttle oder Marathon).</p>'
            '<table><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>')
def set_cycle_units(record, focus, units):
    if units not in CYCLE_UNIT_CHOICES:
        raise ValueError("Bitte 14, 15 oder 16 Einheiten wählen.")
    updated = deepcopy(record)
    settings = updated.setdefault("fussball_schwerpunkte", {})
    if focus not in settings:
        settings[focus] = focus_settings(record, focus)
    settings[focus].setdefault("planung", {})["zyklus_einheiten"] = units
    return updated
def tempo_cycle_position(te, units):
    """Position in der 14er-Laufreihe und Nummer der Steigerungseinheit (0 = keine)."""
    extra = max(0, units - 14)
    if te <= 11:
        return te, 0
    if te <= 11 + extra:
        return 11, te - 11
    return te - extra, 0
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
        if field_text(record.get('Shuttleform')) or field_text(record.get('Strecke je Weg (m)')) or field_text(record.get('Wendezuschlag gesamt (m)')):
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
                    page_index = voice_number_input('Seite der Vorlage', 1, len(document), 1, key='field_ref_page')-1
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
            if band == 'U11' and values['reife'] is None:
                values['reife'] = old.get('reife','Normalentwickler') if old else 'Normalentwickler'
            if old is None and (any(v is None for v in values.values()) or band is None or frequency is None):
                raise ValueError('Für ein neues Profil bitte Alter, Geschlecht, Altersklasse, Gewicht, Körperlänge, Typ und TE pro Woche ausfüllen; ab U13 zusätzlich den Entwicklungsstand.')
            rec = deepcopy(old) if old else {'t_60':None,'sbe':'SR 2'}
            rec.update({k:v for k,v in values.items() if v is not None})
            calendar = band or (old.get('kalenderklasse',calendar_band(rec['alter']))
                               if old and rec['alter'] == old['alter'] else calendar_band(rec['alter']))
            gender = rec.get('geschlecht', 'Weiblich' if rec.get('profil','').endswith('_w') else 'Männlich')
            development = rec['reife']
            saved_assignment = old.get('trainingszuordnung',{}) if old else {}
            same_basis = old and calendar == old.get('kalenderklasse',calendar_band(old['alter'])) and development == old['reife'] and gender == old.get('geschlecht',gender)
            if old:
                rec['geschlecht'] = old.get('geschlecht','Weiblich' if old['profil'].endswith('_w') else 'Männlich')
            else:
                rec['profil'] = storage_profile(football_profile('Fussball_'+calendar,gender),sport)
            rec, assigned, _ = apply_training_assignment(rec,calendar,development,gender,
                saved_assignment.get('veto_klasse') if same_basis else None,
                saved_assignment.get('veto_notiz','') if same_basis else '')
            band = assigned['effective']
            settings = deepcopy(rec.get('fussball_schwerpunkte',{}))
            if old and 'fussball_schwerpunkte' not in old:
                old_focus = legacy_focus(old)
                settings[old_focus] = focus_settings(rec,old_focus)
            active = settings.setdefault(focus, {'planung':{}})
            if frequency is not None:
                active.setdefault('planung',{})['einheiten'] = frequency
            active.setdefault('planung',{}).setdefault('progression',True)
            rec['trainingsschwerpunkt'] = focus
            rec['planung'] = deepcopy(active.get('planung',{}))
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
                labels = {'alter':'Alter','gewicht':'Gewicht (kg)','groesse':'Körpergröße (m)','geschlecht':'Geschlecht',
                    'fasertyp':'Athletentyp','reife':'Entwicklungsstatus','kalenderklasse':'Altersklasse','profil':'Trainingsprofil',
                    'trainingsschwerpunkt':'Trainingsbereich','team':'Team / Trainingsgruppe','t_60':'60-m-Referenz (s)'}
                for key, label in labels.items():
                    if rec.get(key) != old.get(key):
                        before, after = old.get(key), rec.get(key)
                        if key == 'trainingsschwerpunkt':
                            before, after = FOCUS_LABELS.get(before,before), FOCUS_LABELS.get(after,after)
                        diffs.append(f'{label}: {before if before is not None else "leer"} → {after if after is not None else "leer"}')
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
            if not age_matches_profile(rec['alter'],'Fussball_'+calendar):
                notice += '; Alter und Altersklasse laut Stammdaten weichen ab'
            if assigned['blocked']:
                notice += '; benachbarte Planvorlage fehlt: Trainer-Veto erforderlich'
            if rec.get('t_60') is None:
                notice += '; 60-m-Trainingsreferenz noch offen'
            previews.append({'Person':name,'Aktion':'Neu anlegen' if old is None else 'Aktualisieren' if rec_changed else 'Bereits gespeichert',
                'Alter':rec['alter'],'Geschlecht':gender,'Altersklasse':'Ü23 / Master' if calendar=='MASTER' else calendar,
                'Trainingsplan':band if not assigned['blocked'] else 'Trainer-Zuordnung offen','Trainer-Veto':'Ja' if assigned['veto'] else 'Nein',
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
    st.markdown('**Datei auswählen → Vorschau kontrollieren → In den Kader übernehmen.**')
    identities = field_identity_map(st.session_state.kader_db)
    draft = st.session_state.get('roster_draft')
    with st.expander('1. Datei auswählen', expanded=draft is None):
        upload = st.file_uploader('Ausgefüllte Stammdaten- und Testtabelle',type=['xlsx','ods','csv'],key='roster_upload')
        signature = hashlib.sha256(upload.name.encode()+upload.getvalue()).hexdigest() if upload is not None else None
        if upload is None:
            st.session_state.pop('roster_file_signature',None)
        elif signature != st.session_state.get('roster_file_signature'):
            try:
                rows, metadata = read_roster_file(upload.getvalue(),upload.name,identities)
                st.session_state.roster_draft = rows
                st.session_state.roster_pending = metadata
                st.session_state.roster_file_signature = signature
                st.session_state.roster_correct = False
                st.session_state.roster_epoch = st.session_state.get('roster_epoch',0)+1
                st.session_state.pop('roster_preview',None)
                st.session_state.pop('roster_receipt',None)
                st.rerun()
            except Exception as exc:
                st.error(f'Datei nicht eingelesen; nichts übernommen: {exc}')
                return
        if st.button('Leere Erfassung für 30 Personen öffnen'):
            st.session_state.roster_draft = [{**{label:'' for label in ROSTER_LABELS},'Zuordnung':ROSTER_NEW} for _ in range(30)]
            st.session_state.roster_epoch = st.session_state.get('roster_epoch',0)+1
            st.session_state.roster_correct = False
            st.session_state.pop('roster_preview',None)
            st.session_state.pop('roster_receipt',None)
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
    draft = st.session_state.get('roster_draft')
    if draft is None:
        st.info('Wähle oben deine ausgefüllte Tabelle aus. Danach erscheint die Vorschau mit der Schaltfläche zum Übernehmen.')
        return
    st.subheader('2. Vorschau prüfen und in den Kader übernehmen')
    status_area = st.empty()
    correct = st.checkbox('Abweichende vorhandene Stammdaten und Testwerte übernehmen',key='roster_correct',
        help='Nur auswählen, wenn die Werte der Tabelle vorhandene abweichende Angaben ersetzen sollen.') if any(r.get('Zuordnung') in identities for r in draft) else False
    action_area = st.empty()
    with st.expander('Testdatum und Übernahmeoptionen'):
        a,b = st.columns(2)
        datum = a.date_input('Testdatum der Tabelle',key='roster_date')
        team = b.text_input('Team / Trainingsgruppe',max_chars=120,key='roster_team')
        title = st.text_input('Bezeichnung des Testtermins',value='Leistungsanalyse',max_chars=120,key='roster_title')
        focus = st.selectbox('Schwerpunkt für die importierten Personen',list(FOCUS_LABELS),index=1,format_func=FOCUS_LABELS.get,key='roster_focus')
        mode = st.selectbox('Shuttlezeiten ohne Kennzeichnung übernehmen als',FIELD_SHUTTLE_MODES,index=2,key='roster_mode')
        use_reference = st.checkbox('Vorhandene 60-m-Testzeiten als Trainingsreferenz übernehmen',value=True,key='roster_reference')
        st.caption('1 Shuttle = hin UND zurück. Gesamtstrecke = einfache Strecke × 2 × Shuttle-Anzahl + Wendezuschlag für den gesamten Test. Ü23 wird der vorhandenen Trainingsklasse Master zugeordnet.')
    st.caption(f"Testdatum: {datum:%d.%m.%Y} · {team or 'ohne Teamangabe'} · {FOCUS_LABELS[focus]}")
    st.session_state.roster_metadata = {k:st.session_state[k] for k in ('roster_date','roster_team','roster_title','roster_focus','roster_mode')}
    view = st.radio('Tabellenausschnitt',['Stammdaten','Lauftests','Sprungtests','Alle Angaben'],horizontal=True,key='roster_view')
    shared = ['Name','Zuordnung']
    sections = {'Stammdaten':ROSTER_LABELS[1:9],'Lauftests':ROSTER_LABELS[9:15]+['Shuttle-Angabe'],
                'Sprungtests':ROSTER_LABELS[15:18]+['Notiz'],'Alle Angaben':ROSTER_LABELS[1:]}
    epoch = st.session_state.get('roster_epoch',0)
    key = f'roster_grid_{epoch}'
    columns = {label:st.column_config.TextColumn(label,width='small' if label not in ('Name','Notiz','Entwicklungsstand') else 'medium') for label in ROSTER_LABELS}
    profile_labels={ROSTER_NEW:'Neu anlegen',**{identity:'Vorhanden: '+identity for identity in identities}}
    columns['Zuordnung'] = st.column_config.SelectboxColumn('Profil in der App',options=[ROSTER_NEW,*identities],
        format_func=profile_labels.get,width=300,
        help='Neu anlegen: ein neues Athletenprofil speichern. Vorhanden: die Tabellenwerte dieser bereits gespeicherten Person zuordnen.')
    columns['Shuttle-Angabe'] = st.column_config.SelectboxColumn('Shuttle-Angabe',options=['',*FIELD_SHUTTLE_MODES])
    st.markdown('Die zweite Spalte **„Profil in der App“** ergänzt die hochgeladene Tabelle. '
                '**„Neu anlegen“** = ein neues Athletenprofil anlegen. **„Vorhanden: Name“** = das bestehende Profil ergänzen.')
    st.caption('Ist eine Person bereits unter anderer Schreibweise gespeichert, wähle hier ihr vorhandenes Profil. '
               'Leere Angaben ändern vorhandene Stammdaten nicht.')
    edited = st.data_editor(pd.DataFrame(draft).fillna('').astype(str),hide_index=True,width='stretch',height=450,row_height=42,
        column_order=shared+sections[view],column_config=columns,num_rows='fixed',key=key,on_change=roster_sync_grid,args=(key,))
    rows = edited.to_dict('records')
    # Ignore unused template slots, but never drop a row containing an entered value.
    rows = [r for r in rows if any(field_text(r.get(k)) for k in ROSTER_LABELS)]
    st.download_button('Erfassungsentwurf herunterladen (CSV)',roster_csv(rows,datum.isoformat(),title,team,focus,identities),file_name='Doc_Athletic_Kader_und_Tests.csv',mime='text/csv')
    state = dict(rows=rows,datum=datum.isoformat(),bogen=title,focus=focus,team=team,correct=correct,use_reference=use_reference,default_mode=mode)
    fingerprint = hashlib.sha256(json.dumps(state,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    checked = st.session_state.get('roster_preview')
    if not checked or checked['fingerprint'] != fingerprint or checked['revision'] != st.session_state.kader_revision:
        checked = dict(fingerprint=fingerprint,revision=st.session_state.kader_revision,preview=[],changed=0)
        try:
            _, preview, changed = prepare_roster_batch(st.session_state.kader_db,**state)
            checked.update(preview=preview,changed=changed)
        except ValueError as exc:
            checked['error'] = str(exc)
        st.session_state.roster_preview = checked
    new_names = [r['Name'] for r in rows if r.get('Zuordnung') == ROSTER_NEW]
    known_names = [identities[r['Zuordnung']][1] for r in rows if r.get('Zuordnung') in identities]
    with status_area.container():
        if not rows:
            st.info('Trage die Personen unten ein. Anschließend kannst du sie hier in den Kader übernehmen.')
        elif checked.get('error'):
            st.error('Noch nicht übernommen. Bitte diese Angaben prüfen:\n\n'+checked['error'])
            if 'Korrekturoption' in checked['error'] or 'Korrektur ausdrücklich' in checked['error']:
                st.info('Wenn die Tabellenwerte richtig sind, aktiviere direkt darunter „Abweichende vorhandene Stammdaten und Testwerte übernehmen“. Danach wird die Übernahme freigegeben.')
        elif checked['changed']:
            st.warning('Vorschau bereit – diese Änderungen sind noch nicht in der Kaderliste gespeichert.')
        else:
            st.success('Übernahme abgeschlossen: Die Tabellenwerte sind im Kader gespeichert.' if st.session_state.get('roster_receipt') else 'Diese Tabellenwerte sind bereits im Kader gespeichert.')
        if new_names:
            st.write(f"**{len(new_names)} neue Profile:** "+', '.join(new_names))
        if known_names:
            st.write(f"**{len(known_names)} vorhandene Profile:** "+', '.join(known_names))
    with action_area.container():
        if st.button('In den Kader übernehmen',disabled=bool(checked.get('error')) or not checked['changed'],type='primary'):
            try:
                if checked['revision'] != st.session_state.kader_revision:
                    raise StorageConflict('Der Kader hat sich seit der Vorschau geändert. Bitte den gespeicherten Stand neu laden.')
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
                st.session_state.roster_receipt = True
                st.session_state.save_notice = f'Übernahme abgeschlossen: {len(new_names)} neue Profile angelegt; {changed-len(new_names)} vorhandene Profile ergänzt. Die Personen stehen jetzt in der Kaderliste.'
                st.rerun()
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:
                st.error(f'Nicht übernommen: {exc}')
        if rows and not checked.get('error') and not checked['changed']:
            st.button('Kaderliste öffnen',on_click=navigiere,args=('Athleten',))
    if checked['preview']:
        with st.expander('Prüfergebnis und Trainingszuordnung ansehen'):
            st.dataframe(pd.DataFrame(checked['preview']),hide_index=True,width='stretch')
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
        if 'trainingsklasse' in item and item['trainingsklasse'] not in AGE_BANDS:
            raise ValueError('Trainingsklasse des gespeicherten Plans prüfen.')
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
    item = deepcopy(old) if old else {"cycle": cycle, "te": te, "original_plan": plan, "actual": [], "notes": ""}
    item.update(plan=plan, source=source)
    if old is None or plan != old['plan']:
        item['trainingsklasse'] = saved_training_band({'plan':plan}) or (old or {}).get('trainingsklasse') or record['profil'].split('_')[1]
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
        for previous in sessions.values():
            previous.setdefault("schwerpunkt", legacy_focus(record))
        item["schwerpunkt"] = focus
        updated["trainingsschwerpunkt"] = focus
    if old and item == old:
        validate_sessions(sessions)
        return updated
    history = deepcopy(old.get("revisions", [])) if old else []
    if old:
        previous = deepcopy(old)
        previous.pop("revisions", None)
        history.append(previous)
    item.update(saved_at=datetime.now(timezone.utc).isoformat(), revisions=history)
    sessions[key] = item
    validate_sessions(sessions)
    return updated
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
# Dokumentierte Trainerreferenzen; keine automatische Sensorsteuerung.
POWERBAGS = (5,8,10,12,15,17,20)
VBT_KINDS = ('Nicht zugeordnet','Mittlere konzentrische Geschwindigkeit','Spitzengeschwindigkeit')
# Doc Athletic: getrennte Ball-Erwärmung und maximale M-Sprints, 20.09.2026.
M_TRAINING_REVISION = '105-205-305-M-Formen'
M_BALL_EDGES = {'U11': 24., 'U13': 26., 'U15': 28.}
E2_BALL_DISTANCES = (70., 75., 80., 85., 90., 95.)
M_MAX_EDGES = {'U11': (10., 15.), 'U13': (12., 18.), 'U15': (15., 20.)}
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
def m_training_rows(value, sport, band, te, frequency=1, short_day=False):
    config = validate_m_training(value or {}, sport, band)
    rows = []
    ball = config['ball']
    if ball['enabled']:
        technique = ('Ballführung ausschließlich links beziehungsweise rechts; '+('eine Serie je Fuß; ' if band=='U11' else '')+'enge Richtungswechsel.'
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
# Gemeinsame Planungsregeln von Frank Müller, Stand 20.09.2026.
# Nur Planvorlagen: keine Messsperre, keine automatische Geräteansteuerung.
def validate_plan_settings(plan):
    if not isinstance(plan, dict):
        raise ValueError("Ungültige Planung.")
    validate_organization(plan.get("organisation", {}))
    ranges = {"einheiten":(1,2), "startwoche":(1,52), "bag_start":(1,20),
              "burpee_start":(1,30), "cheer_start":(0,30), "single_start":(0,30), "beid_start":(0,30),
              "kreuzheben_last":(0,500), "bag_last":(0,30), "test_distanz":(50,1500), "test_zeit":(0,900),
              "test_prozent":(50,100), "steigerung_wdh":(0,5), "abc_step":(0,10), "abc_start_m":(10,15), "zyklus_einheiten":(14,16)}
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
            validate_assignment(p)
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
            if 'lauftest' in p:
                validate_run_reference(p['lauftest'])
            validate_m_training(p.get("m_training", {}), sport, p["profil"].split("_")[1])
            m_references = p.get('m_lauf_referenzen',[])
            if not isinstance(m_references,list):
                raise ValueError('M-Lauf-Referenzen müssen eine Liste sein.')
            for ref in m_references:
                if not isinstance(ref,dict) or ref.get('klasse') not in AGE_BANDS or ref.get('form') not in ('ball','maximal'):
                    raise ValueError('M-Lauf-Referenz prüfen.')
                if type(ref.get('run_seconds')) not in (int,float) or not math.isfinite(ref['run_seconds']) or not 0 < ref['run_seconds'] <= 3600:
                    raise ValueError('M-Lauf-Referenzzeit prüfen.')
                if type(ref.get('edge_m')) not in (int,float) or not math.isfinite(ref['edge_m']) or not .5 <= ref['edge_m'] <= 100:
                    raise ValueError('M-Lauf-Referenzstrecke prüfen.')
                if ref.get('timed_distance_m') is not None and ref['timed_distance_m'] not in E2_BALL_DISTANCES:
                    raise ValueError('M-Lauf-Durchlaufstrecke prüfen.')
                if not isinstance(ref.get('notes',''),str) or len(ref.get('notes','')) > 4000:
                    raise ValueError('M-Lauf-Referenznotiz prüfen.')
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
            level = p.get("zyklus_einstieg", 1)
            if type(level) is not int or not 1 <= level <= 16:
                raise ValueError("Einstiegsniveau des Makrozyklus prüfen.")
            for field in ("empfehlungen_naechster", "empfehlungen_aktiv"):
                recs = p.get(field, {})
                if not isinstance(recs, dict) or len(recs) > 100 or any(
                        not isinstance(k, str) or len(k) > 60 or not isinstance(v, str) or not 0 < len(v) <= 100000
                        for k, v in recs.items()):
                    raise ValueError("Empfehlungen für den nächsten Makrozyklus prüfen.")
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
def storage_config():
    return StorageConfig(DATABASE_URL, DATA_DIR, DB_FILE, KADER_DATEI)

def lade_kader_von_datei():
    return load_state(storage_config(), DEFAULT_KADER, validate_kader)

def speichere_kader_in_datei(kader, expected_revision):
    return save_state(storage_config(), kader, expected_revision, validate_kader)

def kader_backup_bytes():
    return export_backup(storage_config(), DEFAULT_KADER, validate_kader)

def warmup_text(band, te):
    if band == "U13":
        return "800 m ca. 3:40 min; Einstieg nach Trainerprüfung" if te >= 3 else "Einlaufen nach Trainerentscheidung; 800 m erst etwa ab TE 3"
    return {"U15":"800 m ca. 3:30 min", "U17":"800 m unter 3:15 min",
            "U20":"800 m unter 3:05 min", "U23":"800 m unter 2:55 min"}.get(band,
            "Einlaufen nach Trainerentscheidung; noch keine feste Zeit hinterlegt")
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
        if has_ball_warmup and sport == 'Fussball' and band == 'U11' and row[0] == 'Erwärmung':
            continue  # The specific ball prescription replaces the generic ball warm-up.
        if len(row) != 7: raise ValueError('Trainingsmatrix benötigt sieben Spalten.')
        row = list(row)
        if row[0] == '01 M-Lauf mit Ball':
            index = next((i for i, r in enumerate(warm) if r[0].startswith('Block 1: ABC')), len(warm))
            warm.insert(index, row)
        elif row[0] == 'Erwärmung' or row[0].startswith('Block 1: ABC'):
            if sport == 'Fussball' and band == 'U11' and row[0] == 'Erwärmung':
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
def widget_key(field, sport, mode, target):
    context = json.dumps([sport,mode,target,st.session_state.get("edit_epoch",0)], ensure_ascii=False)
    return field + "_" + hashlib.sha256(context.encode()).hexdigest()[:16]
def reload_saved():
    data, revision = lade_kader_von_datei()
    st.session_state.kader_db = data
    st.session_state.kader_revision = revision
    st.session_state.edit_epoch = st.session_state.get("edit_epoch",0) + 1

def athlete_tempo(record, focus='komplex'):
    if record.get('t_60') is None:
        return []
    source=record.get('t_150_quelle','berechnet')
    t150=record.get('t_150') if source!='berechnet' else round(record['t_60']*2.375,2)
    if t150 is None:
        return []
    test=run_reference(record,focus)
    references=deepcopy(record.get('tempo_referenzen',{}))
    if 'lauftest' in record:
        references.pop(str(test['distanz_m']),None)
    rows=build_tempo_table(record['t_60'],t150,source,references,
                          test['distanz_m'],test['zeit_s'] or 0,True,False)
    if 'lauftest' in record:
        for row in rows:
            if row['Herkunft']=='Referenz: Einzeltest':
                row['Herkunft']='Gemessener Lauftest · '+test['durchfuehrung']
    return rows

RUN_MODES = ['Nicht angegeben','Einzellauf','Gruppenlauf']

def validate_run_reference(test):
    if not isinstance(test,dict) or set(test)!={'distanz_m','zeit_s','durchfuehrung'}:
        raise ValueError('Lauftest: Strecke, gemessene Zeit und Durchführung prüfen.')
    if type(test['distanz_m']) is not int or not 50 <= test['distanz_m'] <= 1500:
        raise ValueError('Laufteststrecke: ganze Meter zwischen 50 und 1500 eingeben.')
    if type(test['zeit_s']) not in (int,float) or not math.isfinite(test['zeit_s']) or not 0 < test['zeit_s'] <= 900:
        raise ValueError('Gemessene Laufzeit: mehr als 0 und höchstens 900 Sekunden eingeben.')
    if test['durchfuehrung'] not in RUN_MODES:
        raise ValueError('Durchführung des Lauftests prüfen.')

def run_reference(record,focus):
    if 'lauftest' in record:
        return deepcopy(record['lauftest'])
    plan=focus_settings(record,focus).get('planung',{})
    return {'distanz_m':int(plan.get('test_distanz',800)),
            'zeit_s':float(plan.get('test_zeit',0)) or None,'durchfuehrung':'Nicht angegeben'}

def run_reference_text(test):
    seconds=f"{test['zeit_s']:g}".replace('.',',')
    mode='' if test['durchfuehrung']=='Nicht angegeben' else ' · '+test['durchfuehrung']
    return f"Gemessener Lauftest: {test['distanz_m']} m in {seconds} s{mode}."

def save_run_reference(record,distance,seconds,mode,unit=None):
    test={'distanz_m':distance,'zeit_s':seconds,'durchfuehrung':mode}
    validate_run_reference(test)
    updated=deepcopy(record)
    updated['lauftest']=test
    if unit is not None:
        cycle,te,focus=unit
        saved=updated.get('einheitenprotokoll',{}).get(focus_unit_key(updated,cycle,te,focus))
        if saved:
            # Only the selected plan's unambiguous automatic test line is corrected.
            # Other units, trainer text, performed values and the original stay intact.
            old=rf'Testauswertung \(keine Laufvorgabe\): {distance} m: \d+(?:[.,]\d+)? s bei \d+(?:[.,]\d+)?% der gemessenen Testgeschwindigkeit'
            current=rf'Gemessener Lauftest: {distance} m in \d+(?:[.,]\d+)? s(?: · (?:Einzellauf|Gruppenlauf))?\.'
            plan=re.sub(rf'(?m)^(?:{old}|{current})$',lambda match:run_reference_text(test),saved['plan'])
            if plan!=saved['plan']:
                updated=save_unit_record(updated,cycle,te,plan,'Lauftest-Korrektur',focus=focus)
    return updated

def render_run_reference_editor(record,sport,name,unit=None):
    focus=unit[2] if unit else legacy_focus(record)
    key=lambda field:widget_key(field,sport,'lauftest_'+focus,name)
    guest=st.session_state.auth_modus=='gast'
    test=run_reference(record,focus)
    if test['zeit_s']:
        st.caption(run_reference_text(test))
    if st.button('Lauftest eintragen oder korrigieren',key=key('open_button'),disabled=guest):
        st.session_state[key('open')]=not st.session_state.get(key('open'),False)
    if not st.session_state.get(key('open')) or guest:
        return
    a,b,c=st.columns(3)
    errors=[]
    distance=voice_number_input('Laufteststrecke (m)',50,1500,test['distanz_m'],key=key('distance'),container=a,validation_errors=errors)
    seconds=voice_number_input('Gemessene Laufzeit (Sekunden)',0.01,900.,test['zeit_s'],key=key('seconds'),container=b,validation_errors=errors)
    mode=c.selectbox('Durchführung des Lauftests',RUN_MODES,index=RUN_MODES.index(test['durchfuehrung']),key=key('mode'))
    st.caption('Gemessene Zeit eingeben, z. B. 48,4. Die Laufreferenz gilt für beide Trainingsbereiche.')
    if unit:
        st.caption('Im angezeigten gespeicherten Plan wird eine passende automatisch erzeugte Testzeile ebenfalls korrigiert; die vorherige Fassung bleibt im Verlauf.')
    if st.button('Lauftest speichern',key=key('save'),disabled=bool(errors)):
        try:
            updated=save_run_reference(record,distance,seconds,mode,unit)
            persist_record(sport,name,updated,'Lauftest gespeichert: '+run_reference_text(updated['lauftest']))
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))

def current_assignment(record):
    gender=record.get('geschlecht','Weiblich' if record['profil'].endswith('_w') else 'Männlich')
    cfg=record.get('trainingszuordnung',{})
    return apply_training_assignment(record,record.get('kalenderklasse',calendar_band(record['alter'])),
                                     record['reife'],gender,cfg.get('veto_klasse'),cfg.get('veto_notiz',''))

def persist_record(sport, name, record, message):
    if st.session_state.auth_modus!='trainer':
        raise StorageError('Speichern ist nur im Trainerzugang möglich.')
    updated=deepcopy(st.session_state.kader_db); updated[sport][name]=record
    rev=speichere_kader_in_datei(updated,st.session_state.kader_revision)
    st.session_state.kader_db=updated;st.session_state.kader_revision=rev
    st.session_state.active_athlete=json.dumps([sport,name],ensure_ascii=False)
    st.session_state.edit_epoch=st.session_state.get('edit_epoch',0)+1
    st.session_state.save_notice=message
    st.rerun()

def select_person(page, allow_new=False):
    choices=[json.dumps(pair,ensure_ascii=False) for pair in roster_options(st.session_state.kader_db)]
    options=(['__new__'] if allow_new else [])+choices
    if not options:
        return None
    current=st.session_state.get('active_athlete')
    labels={value:roster_label(json.loads(value),st.session_state.kader_db) for value in choices}
    labels['__new__']='Neuen Athleten anlegen'
    selected=st.selectbox('Athlet',options,index=options.index(current) if current in options else 0,
                         format_func=labels.get,
                         key=page+'_person_'+str(st.session_state.get('edit_epoch',0)))
    if selected=='__new__':
        return 'Fussball',None,None
    st.session_state.active_athlete=selected
    sport,name=json.loads(selected)
    return sport,name,st.session_state.kader_db[sport][name]

def render_athlete_editor(selection=None,unit=None):
    inline=selection is not None
    if not inline:
        st.header('Athletenprofil · anlegen und bearbeiten')
        selection=select_person('editor',True)
    sport,old_name,old=selection
    record=old or {'alter':None,'gewicht':None,'groesse':None,'t_60':None,'fasertyp':'Schnelligkeit (Sprint)',
                  'reife':'Normalentwickler','geschlecht':'Männlich','sbe':'SR 2'}
    guest=st.session_state.auth_modus=='gast'
    key=lambda f:widget_key(f,sport,'editor',old_name or '__new__')
    name=old_name if inline and old else st.text_input('Name',old_name or '',key=key('name'),disabled=guest or old is not None).strip()
    personal,measurements,development_column,references=st.columns(4)
    with personal:
        age=voice_number_input('Alter (Jahre)',9,40,record['alter'],key=key('age'),disabled=guest)
        gender=st.selectbox('Geschlecht',['Männlich','Weiblich'],index=int(record.get('geschlecht','Weiblich' if record.get('profil','').endswith('_w') else 'Männlich')=='Weiblich'),key=key('gender'),disabled=guest)
    with measurements:
        height=voice_number_input('Körpergröße (m)',1.3,2.15,record['groesse'],key=key('height'),disabled=guest)
        weight=voice_number_input('Körpergewicht (kg)',30.,140.,record['gewicht'],key=key('weight'),disabled=guest)
    with development_column:
        kinds=['Ausdauer','Kraft','Sprungkraft','Gazelle','Schnelligkeit (Sprint)']
        kind=st.selectbox('Athletentyp',kinds,index=kinds.index(record['fasertyp']),key=key('type'),disabled=guest)
        calendar=(record.get('kalenderklasse',calendar_band(age)) if old and age==old['alter'] else calendar_band(age)) if age is not None else None
        development=record['reife']
        if calendar and calendar!='U11':
            options=['Spätentwickler (Retardiert)','Normalentwickler','Frühentwickler (Akzeleriert)']
            development=st.selectbox('Entwicklungsstatus',options,index=options.index(development),key=key('development'),disabled=guest)
        elif calendar=='U11':
            st.caption('U11: regulärer Plan ohne entwicklungsabhängige Verschiebung.')
    with references:
        frequency=st.selectbox('Einheiten pro Woche',[1,2],index=int(record.get('planung',{}).get('einheiten',1))-1,key=key('frequency'),disabled=guest)
        t60=voice_number_input('60m-Referenz (s; falls vorhanden)',6.,15.,record.get('t_60'),key=key('t60'),disabled=guest)
    notes=st.text_input('Profilnotiz (optional)',record.get('notizen',''),max_chars=4000,key=key('notes'),disabled=guest)
    cfg=record.get('trainingszuordnung',{})
    same=old and calendar==record.get('kalenderklasse',calendar_band(old['alter'])) and development==record['reife'] and gender==record.get('geschlecht',gender)
    veto=cfg.get('veto_klasse') if same else None
    veto_note=cfg.get('veto_notiz','') if veto else ''
    st.caption('Profiländerungen mit „Athletenprofil speichern“ übernehmen. Die Trainingsmatrix verwendet den gespeicherten Stand.')
    veto_action,save_action=st.columns(2)
    save_veto=False
    if calendar:
        assignment=training_assignment(calendar,development,veto)
        st.caption(f"Altersklasse {calendar} → Trainingsplan {assignment['effective']}"+(' · Trainer-Veto' if veto else ''))
        opened=key('veto_open')+'_'+calendar+'_'+development+'_'+gender
        if veto_action.button('Trainer-Veto zur Trainingsklasse',disabled=guest,key=key('veto_button')):
            st.session_state[opened]=not st.session_state.get(opened,False)
        if st.session_state.get(opened):
            options=['Automatisch']+list(AGE_BANDS)
            choice=st.selectbox('Trainingsklasse nach Trainer-Veto',options,index=options.index(veto or 'Automatisch'),key=opened+'_class')
            veto=None if choice=='Automatisch' else choice
            veto_note=st.text_input('Trainer-Notiz zur Zuordnung (optional)',veto_note,max_chars=4000,key=opened+'_note') if veto else ''
            selected=training_assignment(calendar,development,veto)
            st.caption(f"Ausgewählt: Trainingsplan {selected['effective']}. Mit „Trainer-Veto anwenden“ speichern.")
            save_veto=st.button('Trainer-Veto anwenden',type='primary',disabled=guest,key=opened+'_apply')
    save_profile=save_action.button('Athletenprofil speichern',type='primary',disabled=guest)
    if save_profile or save_veto:
        try:
            if not name or age is None or weight is None or height is None:
                raise ValueError('Name, Alter, Körpergewicht und Körpergröße bitte eintragen.')
            if old is None and any(name in people for people in st.session_state.kader_db.values()):
                raise ValueError('Der Name ist bereits vorhanden. Bitte das vorhandene Profil auswählen.')
            updated=deepcopy(record)
            updated.update(alter=age,gewicht=weight,groesse=height,fasertyp=kind,notizen=notes,t_60=t60)
            updated.setdefault('profil',storage_profile(football_profile('Fussball_'+calendar,gender),sport))
            updated,_,_=apply_training_assignment(updated,calendar,development,gender,veto,veto_note)
            updated.setdefault('planung',{})['einheiten']=frequency
            for settings in updated.get('fussball_schwerpunkte',{}).values():
                settings.setdefault('planung',{})['einheiten']=frequency
            if updated.get('t_150_quelle','berechnet')=='berechnet':
                updated.pop('t_150',None)
                if t60 is not None:updated['t_150']=round(t60*2.375,2)
            persist_record(sport,name,updated,f"Athletenprofil gespeichert · Trainingsplan {updated['profil'].split('_')[1]}.")
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    if old:
        render_run_reference_editor(old,sport,old_name,unit)
        with st.expander('Gespeicherte Messungen und Profilverlauf'):
            render_field_history(old)
            if old.get('sprungtests'):st.dataframe(pd.DataFrame([jump_summary(t) for t in old['sprungtests']]),hide_index=True)
            if old.get('m_lauf_referenzen'):st.dataframe(pd.DataFrame(old['m_lauf_referenzen']),hide_index=True)

def change_cycle(record, name, restore=False):
    updated=deepcopy(record); active=updated.get('aktiver_makrozyklus','Bestand')
    archive=deepcopy(updated.get('makrozyklen',{}))
    if not name or len(name)>120 or name==active or (not restore and name in archive):
        raise ValueError('Bitte einen anderen, eindeutigen Zyklusnamen eingeben.')
    snapshot={k:deepcopy(v) for k,v in updated.items() if k not in ('makrozyklen','aktiver_makrozyklus','einheitenprotokoll')}
    if restore:
        if name not in archive:raise ValueError('Makrozyklus nicht vorhanden.')
        restored=archive.pop(name)
        if restored.get('profil')==updated.get('profil'):
            for k in ('planung','phasensteuerung','fussball_schwerpunkte','m_training'):
                if k in restored:updated[k]=deepcopy(restored[k])
                else:updated.pop(k,None)
    else:
        updated['phasensteuerung']=phase_defaults()
        updated.setdefault('planung',{}).update(startwoche=1,progression=True)
        # Frank, 25.09.2026: Einstieg U11–U15 auf Niveau TE 10, ab U17 TE 8; Trainer-Veto.
        band=updated.get('profil','Fussball_U15').split('_')[1]
        updated['zyklus_einstieg']=10 if band in ('U11','U13','U15') else 8
        updated['empfehlungen_aktiv']=updated.pop('empfehlungen_naechster',{})
    archive[active]=snapshot
    updated.update(makrozyklen=archive,aktiver_makrozyklus=name)
    return updated

def render_cycle_controls(record,sport,name,key):
    level=int(record.get('zyklus_einstieg',1))
    chosen=st.selectbox('Einstieg dieses Zyklus auf dem Niveau von',list(range(1,17)),index=level-1,
        format_func=lambda n:f'TE {n}' if n>1 else 'TE 1 (Grundniveau)',key=key('cycle_level'),
        help='Neuer Zyklus: U11–U15 wie TE 10, ab U17 wie TE 8. Per Trainer-Veto änderbar.')
    if chosen!=level and st.button('Einstieg speichern',key=key('cycle_level_save')):
        try:
            updated=deepcopy(record);updated['zyklus_einstieg']=chosen
            persist_record(sport,name,updated,f'Einstieg auf Niveau TE {chosen} gespeichert.')
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    cycle_name=st.text_input('Name des neuen Makrozyklus',key=key('cycle_name'))
    if st.button('Neuen Makrozyklus beginnen',key=key('cycle_new')):
        try:persist_record(sport,name,change_cycle(record,cycle_name.strip()),'Neuer Makrozyklus begonnen.')
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    if record.get('makrozyklen'):
        chosen=st.selectbox('Gespeicherten Makrozyklus aufrufen',list(record['makrozyklen']),key=key('cycle_old'))
        if st.button('Makrozyklus aufrufen',key=key('cycle_restore')):
            try:persist_record(sport,name,change_cycle(record,chosen,True),'Makrozyklus geöffnet.')
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))

def saved_training_band(item):
    if item.get('trainingsklasse') in AGE_BANDS:
        return item['trainingsklasse']
    text='\n'.join(line for line in item.get('plan','').splitlines() if not re.match(r'^\s*(?:Begründung|Traineranweisung)\s*:',line))
    bands=re.findall(r'\bTrainingsplan\s*:?\s*(U11|U13|U15|U17|U20|U23|MASTER)\b',text)
    if not bands:
        bands=re.findall(r'\b(U11|U13|U15|U17|U20|U23|MASTER)[ -]Plan\b',text)
    return bands[0] if bands and len(set(bands))==1 else None

def unit_has_results(item):
    return bool(item.get('performed') or item.get('actual') or item.get('notes') or
        any(item.get('timing',{}).get(k) is not None for k in ('actual_athletic_min','actual_transfer_min')))

def split_trainer_instructions(plan):
    lines, instructions = [], []
    band=saved_training_band({'plan':plan})
    for line in plan.splitlines():
        if re.match(r'^\s*(?:Begründung|Traineranweisung)\s*:',line):
            instructions.append(line.strip())
            continue
        suffix='. Trainer-Veto und individuelle Eignungsprüfung bleiben möglich.'
        if line.startswith('Altersklasse ') and line.endswith(suffix):
            instructions.append(suffix[2:])
            line=line[:-len(suffix)]
        if band and band!='U11':
            line=line.replace('bei U11 eine Serie je Fuß; ','')
        lines.append(line)
    return '\n'.join(lines), instructions

def saved_plan_html(plan):
    """Gespeicherten Plan darstellen; alte ABC-Bezeichnung angleichen, Werte erhalten."""
    headers=[['Block / Phase','Trainingsmittel / Übung','Sätze','Wdh. / Distanz',
              'Hardware / Zusatzlast','Intensität','Pause'],
             ['Abschnitt','Soll','Ist','Abweichung']]
    lines=split_trainer_instructions(plan)[0].splitlines()
    def cells(line):
        stripped=line.strip()
        return [part.strip() for part in stripped[:-1].split('|')] if stripped.endswith('|') else None
    rendered=[]; index=0
    while index<len(lines):
        header=None; consumed=0
        for candidate in headers:
            if cells(lines[index])==candidate:
                header,consumed=candidate,1
                break
            if [cells(line) for line in lines[index:index+len(candidate)]]==[[label] for label in candidate]:
                header,consumed=candidate,len(candidate)
                break
        if header:
            rows=[]; end=index+consumed
            while end<len(lines):
                row=cells(lines[end])
                if row is None or len(row)!=len(header):
                    break
                if len(row)==7 and row[0]=='Block 1: ABC':
                    old_label=re.fullmatch(r'2 (?:Bahnen|Shuttle) insgesamt(; je einmal in beide Richtungen)?',row[2])
                    if old_label:
                        row[2]='2 × Shuttle'
                        if old_label[1] and old_label[1].lstrip('; ') not in row[3]:
                            row[3]+=old_label[1]
                rows.append(row); end+=1
            if rows:
                rendered.append('<div class="plan-table"><table><thead><tr>'+''.join(
                    '<th scope="col">'+escape(label)+'</th>' for label in header)+'</tr></thead><tbody>'+''.join(
                    '<tr>'+''.join('<td>'+escape(value)+'</td>' for value in row)+'</tr>' for row in rows
                    )+'</tbody></table></div>')
                index=end
                continue
        # Unklare Tabellenzeilen und freie Trainertexte bleiben wortgetreu lesbar.
        tag='h3' if lines[index].startswith('TRAININGSMATRIX - EINHEIT:') else 'p'
        rendered.append('<'+tag+'>'+escape(lines[index])+'</'+tag+'>')
        index+=1
    return '<section class="doc-saved-plan" data-saved-plan="true">'+''.join(rendered)+'</section>'

def export_plan(plan):
    return ('<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Doc Athletic Trainingsplan</title>'
            '<style>body{font-family:Arial}@media print{@page{size:A4 landscape}}'+SAVED_PLAN_STYLE+'</style></head>'
            '<body><h1>Doc Athletic Train Smart Evolution</h1>'+saved_plan_html(plan)+'</body></html>')

def render_training():
    st.header('Athletenprofil & Trainingsschwerpunkt')
    person_column,focus_column,unit_column=st.columns([1.25,2,0.8])
    with person_column:
        selection=select_person('training')
    if selection is None:
        st.info('Zuerst einen Athleten anlegen oder unter Tests / Import eine Liste einlesen.')
        render_athlete_editor()
        return
    sport,name,stored=selection
    record,assignment,_=current_assignment(stored)
    guest=st.session_state.auth_modus=='gast'
    with focus_column:
        focus=st.radio('Trainingsbereich',list(FOCUS_LABELS),format_func=FOCUS_LABELS.get,horizontal=True,key='training_focus')
    cycle=record.get('aktiver_makrozyklus','Bestand')
    band=record['profil'].split('_')[1]
    cfg,total,units_now=cycle_plan(record,focus,band)
    with unit_column:
        chosen_units=st.selectbox('Einheiten im Halbjahr',CYCLE_UNIT_CHOICES,index=CYCLE_UNIT_CHOICES.index(units_now),
            key=widget_key('cycle_units',sport,focus,name),disabled=guest,
            help='Standard 16. Die letzte Einheit ist immer der Retest für den Jahresvergleich.')
    if chosen_units!=units_now and not guest:
        try:persist_record(sport,name,set_cycle_units(record,focus,chosen_units),f'Halbjahr auf {chosen_units} Einheiten eingestellt.')
        except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    archived_units={item['te'] for item in record.get('einheitenprotokoll',{}).values()
                    if item.get('cycle')==cycle and item.get('schwerpunkt',legacy_focus(record))==focus}
    options=sorted(set(range(1,total+1))|archived_units)
    with unit_column:
        te=st.selectbox('Trainingseinheit (TE)',options,format_func=lambda n:f'TE {n} · Retest' if n==units_now else f'TE {n}',key='training_te')
    with st.container(border=True):
        render_athlete_editor(selection,(cycle,te,focus))
    saved=record.get('einheitenprotokoll',{}).get(focus_unit_key(record,cycle,te,focus))
    key=lambda field:widget_key(field,sport,focus+'_'+cycle+'_'+str(te),name)
    st.caption(f"{cycle} · {record['kalenderklasse']} → Trainingsplan {record['profil'].split('_')[1]} · {record['fasertyp']}")
    if assignment['blocked'] and not saved:
        st.info('Für diese Zuordnung fehlt eine benachbarte Planvorlage. Oben über das Trainer-Veto eine Trainingsklasse festlegen.')
        return
    planned,effective=phase_status(cfg,band,te)
    if planned!=effective and effective!='Zyklus abgeschlossen' and not guest and not saved and not (band=='U15' and effective=='Jumps'):
        flag='jumps_ready' if not cfg['jumps_ready'] else 'spruenge_ready'
        stage='Jumps' if flag=='jumps_ready' else 'Sprünge'
        st.caption(f'Vorgesehen: {planned}. Bis zur Trainerfreigabe gilt {effective}.')
        if st.button('Phasenwechsel zu '+stage+' freigeben',key=key('phase_release')):
            try:
                record.setdefault('phasensteuerung',{})[flag]=True
                persist_record(sport,name,record,'Phasenwechsel für neue Vorlagen freigegeben.')
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    if not guest:
        with st.expander('Kraftphasen dieses Athleten (Trainer-Veto)'):
            st.caption('Standard: Stand 6 · Jumps 5 · Sprünge 5. Früher oder später wechseln, je nach Athlet.')
            stored=record.get('phasensteuerung',{})
            base=phase_defaults();base.update(stored)
            a,b,c=st.columns(3)
            lengths=[x.selectbox(label,list(range(1,15)),index=base[k]-1,key=key('phase_'+k))
                     for x,label,k in ((a,'Stand (TE)','basis'),(b,'Jumps (TE)','jumps'),(c,'Sprünge (TE)','spruenge'))]
            u11=st.checkbox('U11: Sprünge auf der Stelle freigeben',value=bool(base.get('u11_spruenge')),key=key('phase_u11')) if band=='U11' else bool(base.get('u11_spruenge'))
            if st.button('Kraftphasen speichern',key=key('phase_save')):
                try:
                    updated=deepcopy(record)
                    updated.setdefault('phasensteuerung',{}).update(basis=lengths[0],jumps=lengths[1],spruenge=lengths[2],u11_spruenge=u11,jumps_ready=True,spruenge_ready=True)
                    phase_validate(updated['phasensteuerung'])
                    persist_record(sport,name,updated,f'Kraftphasen gespeichert: Stand {lengths[0]} · Jumps {lengths[1]} · Sprünge {lengths[2]}.')
                except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
    generated=generate_unit(record,focus,te,name)
    standard_text=plan_as_text(generated)
    recommendation=record.get('empfehlungen_aktiv',{}).get(f'{focus}|{te}')
    if recommendation and not saved:
        st.info('Für diese Einheit liegt deine Empfehlung aus dem vorherigen Makrozyklus vor. Sie hat Vorrang vor der Tabellenvorlage.')
        generated=saved_plan_html(recommendation);standard_text=recommendation
    template_view=False
    completed=unit_has_results(saved) if saved else False
    saved_band=saved_training_band(saved) if saved else None
    if saved and saved_band!=band:
        st.info(f"Aktuelle Trainingsklasse: {band}. Gespeicherter Plan: {saved_band or 'Klasse nicht hinterlegt'}.")
        views=[f'Aktueller {band}-Plan',f'Gespeicherter {saved_band}-Plan' if saved_band else 'Gespeicherter Sollplan']
        view=st.radio('Angezeigter Plan',views,index=1 if completed else 0,horizontal=True,key=key('plan_view'))
        template_view=view==views[0]
    current=standard_text if not saved or template_view else saved['plan']
    if template_view:
        st.caption(f'Aktuelle {band}-Vorlage. Der bisherige Sollplan bleibt gespeichert, bis du die neue Vorlage übernimmst.')
    elif saved:
        st.caption('Gespeicherter Sollplan'+(' · Durchführung dokumentiert.' if completed else '.'))
    if current==standard_text:st.markdown(generated,unsafe_allow_html=True)
    else:st.markdown(saved_plan_html(current),unsafe_allow_html=True)
    _, instructions=split_trainer_instructions(current)
    with st.container(key='trainer_instructions'):
        with st.expander('Traineranweisung'):
            st.write(f"Altersklasse {record['kalenderklasse']} · {record['reife']} · Trainingsplan {band}.")
            note=record.get('trainingszuordnung',{}).get('veto_notiz')
            if note:st.write(note)
            for instruction in instructions:st.write(instruction)
            if 'Trainer-Veto und individuelle Eignungsprüfung bleiben möglich.' not in instructions:
                st.write('Trainer-Veto und individuelle Eignungsprüfung bleiben möglich.')
    key=lambda field:widget_key(field,sport,focus+'_'+cycle+'_'+str(te)+('_vorlage' if template_view else '_sollplan'),name)
    editable=not (template_view and completed)
    if template_view and completed:
        st.caption('Die dokumentierte Durchführung gehört zum gespeicherten Plan. Für eine neue Durchführung eine offene Einheit wählen.')
    if not guest:
        if st.button(f'Als Empfehlung für TE {te} im nächsten Makrozyklus speichern',key=key('recommend')):
            try:
                updated=deepcopy(record)
                updated.setdefault('empfehlungen_naechster',{})[f'{focus}|{te}']=current
                persist_record(sport,name,updated,f'Empfehlung für TE {te} des nächsten Makrozyklus gespeichert.')
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
        if not saved and st.button('Einheit speichern',type='primary',key=key('save')):
            try:persist_record(sport,name,save_unit_record(record,cycle,te,current,'Standardplan',focus=focus),'Einheit gespeichert.')
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
        if template_view and not completed and st.button(f'{band}-Plan für diese Einheit übernehmen',type='primary',key=key('adopt')):
            try:
                updated=save_unit_record(record,cycle,te,standard_text,'Trainer-Zuordnung',focus=focus)
                persist_record(sport,name,updated,f'{band}-Plan übernommen. Die vorherige Fassung bleibt im Verlauf.')
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
        for label,field in [('Trainer-Veto für diese Einheit','veto'),('Durchführung notieren','actual'),('Makrozyklus verwalten','cycle')]:
            if field!='cycle' and not editable:continue
            if st.button(label,key=key(field+'_button')):
                st.session_state[key(field+'_open')]=not st.session_state.get(key(field+'_open'),False)
        if editable and st.session_state.get(key('veto_open')):
            edited=st.text_area('Verbindlicher Sollplan dieser Einheit',current,height=400,max_chars=100000,key=key('veto_text'))
            st.caption('Die geänderte Fassung ersetzt den Sollplan dieser Einheit. Andere Einheiten bleiben unverändert.')
            if st.button('Trainer-Veto speichern',key=key('veto_save')):
                try:
                    if not edited.strip():raise ValueError('Der Sollplan darf nicht leer sein.')
                    updated=record if saved else save_unit_record(record,cycle,te,standard_text,'Standardplan',focus=focus)
                    if edited!=current:updated=save_unit_record(updated,cycle,te,edited,'Trainer-Veto',focus=focus)
                    persist_record(sport,name,updated,'Trainer-Veto gespeichert.')
                except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
        if editable and st.session_state.get(key('actual_open')):
            performed=st.date_input('Durchgeführt am',date.fromisoformat(saved.get('performed',date.today().isoformat())) if saved else date.today(),key=key('performed'))
            note=st.text_area('Beobachtung / Belastung / Abweichung',saved.get('notes','') if saved else '',max_chars=4000,key=key('actual_note'))
            actual=saved.get('actual',[]) if saved else []
            actual_error=False
            if st.button('Einzelwerte erfassen oder korrigieren',key=key('values_button')):st.session_state[key('values_open')]=True
            if st.session_state.get(key('values_open')):
                rows=actual or [{'Übung':'',**{k:None for k in NUMERIC_COLUMNS},'Technik':'Nicht bewertet','Belastung':'Nicht bewertet','Anmerkung':''}]
                frame=pd.DataFrame(rows,columns=PROTOCOL_COLUMNS)
                for col in NUMERIC_COLUMNS:frame[col]=pd.to_numeric(frame[col],errors='coerce').astype(float)
                columns={k:st.column_config.NumberColumn(k,min_value=0) for k in NUMERIC_COLUMNS}
                columns['Technik']=st.column_config.SelectboxColumn(options=['Nicht bewertet','Sauber','Unsicher'])
                columns['Belastung']=st.column_config.SelectboxColumn(options=['Nicht bewertet','Gut bewältigt','Grenzwertig','Nicht bewältigt'])
                frame=st.data_editor(frame,column_config=columns,num_rows='dynamic',hide_index=True,key=key('values'))
                try:actual=protocol_rows(frame)
                except ValueError as exc:st.error(str(exc));actual_error=True
            if st.button('Durchführung speichern',key=key('actual_save'),disabled=actual_error):
                try:
                    updated=save_unit_record(record,cycle,te,current,'Trainer-Zuordnung' if template_view else saved['source'] if saved else 'Standardplan',actual=actual,notes=note,performed=performed.isoformat(),focus=focus)
                    persist_record(sport,name,updated,'Durchführung gespeichert; fehlende Einzelwerte wurden nicht ergänzt.')
                except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))
        if st.session_state.get(key('cycle_open')):render_cycle_controls(record,sport,name,key)
    if saved and saved.get('revisions'):
        with st.expander('Frühere Fassungen dieser Einheit'):
            for item in reversed(saved['revisions']):st.markdown(saved_plan_html(item['plan']),unsafe_allow_html=True)
    if st.button('Tempotabelle 50–800 m ansehen',key=key('tempo_button')):
        st.session_state[key('tempo_open')]=not st.session_state.get(key('tempo_open'),False)
    if st.session_state.get(key('tempo_open')):
        tempo=athlete_tempo(record,focus)
        if tempo:st.dataframe(pd.DataFrame(tempo),hide_index=True)
        else:st.info('Noch keine Sprintreferenz vorhanden. Trainingsplan und Speicherung sind trotzdem verfügbar.')
    st.download_button('Diesen Trainingsplan herunterladen',export_plan(current),file_name=f'Doc_Athletic_TE{te}.html',mime='text/html')

def render_backup():
    st.header('Datensicherung')
    st.download_button('Kader sichern (Backup-Datei)',data=kader_backup_bytes,file_name='kader_db.json',mime='application/json',on_click='ignore')
    if st.button('Gespeicherten Stand neu laden'):
        try:reload_saved();st.rerun()
        except (ValueError,OSError,sqlite3.Error,StorageError) as exc:st.error(str(exc))
    upload=st.file_uploader('Kader aus Backup laden',type=['json'])
    if upload is not None:
        confirmed=st.checkbox('Enthaltene Kaderdaten durch die Sicherung ersetzen')
        if st.button('Backup jetzt wiederherstellen',disabled=not confirmed):
            try:
                candidate=restore_kader_backup(decode_backup(upload.getvalue(),validate_kader),st.session_state.kader_db)
                rev=speichere_kader_in_datei(candidate,st.session_state.kader_revision)
                st.session_state.kader_db=candidate;st.session_state.kader_revision=rev
                st.session_state.edit_epoch=st.session_state.get('edit_epoch',0)+1
                st.session_state.save_notice='Kader wiederhergestellt.';st.rerun()
            except (ValueError,OSError,sqlite3.Error,StorageError,StorageConflict) as exc:st.error(str(exc))


def generate_unit(record, focus, te, name="Athlet"):
    """Eine Standardvorlage; keine UI, keine Schreibzugriffe, keine Zukunftsprognose."""
    if focus not in FOCUS_LABELS or type(te) is not int or not 1 <= te <= 28:
        raise ValueError("Schwerpunkt oder Einheit unbekannt.")
    aktuelle_daten=record
    ziel=name
    band=record['profil'].split('_')[1]
    geschlecht_wahl=record.get('geschlecht','Weiblich' if record['profil'].endswith('_w') else 'Männlich')
    ft=record['fasertyp']; gewicht=record['gewicht']
    plan_age=profile_age(record['profil'])
    speed_mode=focus=='speed_jump'
    saved=focus_settings(record,focus).get('planung',{})
    einheiten=int(saved.get('einheiten',1)); startwoche=1; role='Automatisch nach Wochenrhythmus'
    phase_config,speed_total_units,cycle_length=cycle_plan(record,focus,band)
    speed_config=speed_jump_defaults(band,geschlecht_wahl)
    hurdle_config=hurdle_defaults(); m_config=m_training_defaults('Fussball',band); org_config={}
    # Previously documented exercise starts remain references, not extra setup questions.
    cheer_start=int(saved.get('cheer_start',0)); single_start=int(saved.get('single_start',0)); bilateral_start=int(saved.get('beid_start',0))
    test=run_reference(record,focus)
    calendar=record.get('kalenderklasse',calendar_band(record['alter']))
    assignment_text=f"Altersklasse {calendar} → Trainingsplan {band}"
    if record.get('trainingszuordnung',{}).get('veto_klasse'):
        assignment_text+=' · Trainer-Veto'
    bag_text = powerbag_load(band, geschlecht_wahl)
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
    hex_text = kreuzheben_load(band, 0)
    strength_exercise = "Kreuzhebe-Streckung"
    if band == "U13" or (band == "U15" and geschlecht_wahl == "Weiblich"):
        strength_exercise = "Anreiß-Jumps / Anreiß-Sprünge (Powerbag)"
        hex_text = ("Powerbag 5–8 kg" if geschlecht_wahl == "Weiblich" else "Powerbag 8–12 kg") if band == "U13" else "Powerbag 10–15 kg"
    elif band not in ["U11", "U13"]:
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
    te_num=te
    planned_phase,effective_phase=phase_status(phase_config,band,te_num)
    bag_exercise="Front Squat Jumps / Anreiß-Sprünge"
    if band == "U11":
        strength_exercise = "Kreuzhebesprünge auf der Stelle"
        hex_text = "2 kg je Kurzhantel"
        bag_exercise = "Front Squat Jumps"
        bag_text = "2 kg je Kurzhantel"
    if te_num == cycle_length:
        return retest_html(band, geschlecht_wahl, bag_text, gb_last_kg, ziel, aktuelle_daten.get("aktiver_makrozyklus", "Bestand"))
    if effective_phase=="Zyklus abgeschlossen":
        html_matrix=f'<div class="druck-block"><h3>TRAININGSMATRIX - EINHEIT: TE {te_num}</h3><p>Außerhalb des konfigurierten Makrozyklus. Neuen Zyklus planen oder Phasenlängen ändern. Gespeicherte Soll-/Ist-Protokolle bleiben unten abrufbar.</p></div>'
        return html_matrix
    if effective_phase in ("Grundlast","Jumps","Sprünge"):
        bag_exercise=phase_exercise_label("front_squat",effective_phase)
        kind="anreiss" if band=="U13" or (band=="U15" and geschlecht_wahl=="Weiblich") else "kreuzheben"
        strength_exercise=phase_exercise_label(kind,effective_phase)
    week, day, short_day = unit_context(te_num, einheiten, startwoche, role)
    # Einstieg im Folgezyklus auf höherem Niveau (Frank, 25.09.2026).
    einstieg = int(record.get('zyklus_einstieg', 1))
    level = te_num + einstieg - 1
    week += einstieg - 1
    # Existing 14-block sequence is keyed to TE, never to calendar week.
    # Bei 15/16 Einheiten: Steigerungseinheiten nach TE 11, Test in der letzten TE.
    woche, steigerung = tempo_cycle_position(te_num, cycle_length)
    abc_rows = abc_rows_115(band, geschlecht_wahl, week, True, 10.0)
    warmup = warmup_text(band, te_num)
    bag_count = weekly_reps(10, week, 15, True)
    quality_day = short_day or speed_mode
    bag_wdh = "8–6–5 Wdh. (3 Sätze)" if quality_day else rep_rule(geschlecht_wahl, level) + " je Satz"
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
        burpee_rep = rep_rule(geschlecht_wahl, level)
        extra_rows += exercise_row("Burpees / Liegestützsprünge mit Strecksprung", "3", burpee_rep, "Powerbar 2–3 kg gesamt" if plan_age >= 14 else "Zusatzlast nicht hinterlegt", f"+1 Wdh./Woche")
        paired = weekly_reps(cheer_start,week,100,True) if cheer_start else 0
        pair_text = f"{paired} links + {paired} rechts = {paired*2} gesamt" if paired else "Start je Seite noch festlegen"
        extra_rows += exercise_row("Cheerleading: beidbeinige Fußgelenksprünge, Arme wechselseitig", "3", pair_text, cheer_load(band,geschlecht_wahl), f"+1 je Seite / Woche")
        paired = weekly_reps(single_start,week,100,True) if single_start else 0
        pair_text = f"{paired} links + {paired} rechts = {paired*2} gesamt" if paired else "Start je Bein noch festlegen"
        extra_rows += exercise_row("Leg Speed Curler einbeinig", "3", pair_text, "Gerätespezifischer Widerstand: aus dokumentierter Ist-Einheit in Sollplan übernehmen", f"+1 je Bein / Woche")
        bilateral = str(weekly_reps(bilateral_start,week,100,True)) + " Wdh." if bilateral_start else "Start noch festlegen"
        extra_rows += exercise_row("Leg Speed Curler beidbeinig", "3", bilateral, "Gerätespezifischer Widerstand: aus dokumentierter Ist-Einheit in Sollplan übernehmen", f"+1 gemeinsame Wdh./Woche")
    abc_last_str = abc_rows[0][4]
    row_abc = rows_html(abc_rows)
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
    if steigerung:
        # Längster Lauf bleibt bei der bisherigen Höchststrecke (600/700/800 m).
        tl_pos = "vor_komplex"
        tl_pause = "100m Gehpause"
        if plan_age <= 15:
            tl_text = f"3 x 600m TL (Richtwert 1:40 min) + {4 + steigerung} x 150m Speed"
        elif plan_age <= 17:
            tl_text = f"GLA vorab: 1 x 700m Kappe + 2 x {min(600, 500 + 50 * steigerung)}m + 3 x 150m Speed"
        else:
            strecke = min(600, 500 + 50 * steigerung)
            tl_text = f"GLA vorab: 800m Basis + 600m, 600m + {strecke}m, {strecke}m (je 100m GP)"
        tl_text += f" · Steigerungseinheit {steigerung} nach TE 11"
    # Frank Müller, 25.09.2026: TE 1–15 Tempolauf-Pyramide nach 50-m-Regel; U11 alaktazid.
    tl_pos = "nach_komplex"
    if band == "U11":
        tl_text = "GL-Ausdauer im Team-Style, locker: " + u11_endurance(level)
        tl_pause = "Staffelform / Team-Style"
    else:
        pyramide = tempo_pyramid(band, geschlecht_wahl, level)
        tl_text = "Tempolauf-Pyramide im Team-Style: " + " + ".join(f"{d} m ({tempo_intensity(d, band)})" for d in pyramide)
        tl_pause = " / ".join("100 m Gehpause" if d >= 300 else "50 m Gehpause" for d in pyramide)
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
    test_note = (run_reference_text(test) if test['zeit_s']
                 else "Tempolauf-Zielzeiten richten sich nach vorhandenen Tests derselben Distanz")
    phase_label = "Komplextraining: Kraft und anschließende Sprints/Läufe"
    if short_day:
        phase_label = "Neuromuskulärer Erinnerungsreiz"
    row_gla_vorab = ""
    if tl_pos == "vor_komplex":
        row_gla_vorab = f'<tr style="background-color: #FCE4D6;"><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold; color: #C00000;">Block 1: GLA Vorab</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; font-weight: bold;">{tl_text}</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">Serie</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">Kaskade vor Kraft</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">–</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9;">60-70% Vmax</td><td style="padding: 6px 8px; border: 1px solid #D9D9D9; text-align: center;">{tl_pause}</td></tr>'
    row_tl_transfer = ""
    row_speed_tempo = ""
    block_rounds = None
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
        phase_label = f"Kraftphase {PHASE_NAMES[effective_phase]} · vorgesehen: {PHASE_NAMES.get(planned_phase, planned_phase)}"
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
    <h3 style="margin: 0; color: #66fcf1 !important;">TRAININGSMATRIX - EINHEIT: TE {te_num}</h3>
    <span style="color: #ffb703; font-weight: bold; font-size: 14px;">{phase_label}</span>
    </div>
    <p style="color: #ffffff !important; font-size: 14px; margin-top: 8px;"><strong>Schwerpunkt:</strong> {escape(FOCUS_LABELS[focus])} | <strong>Makrozyklus:</strong> {escape(aktuelle_daten.get("aktiver_makrozyklus", "Bestand"))} | <strong>Athlet:</strong> {escape(ziel)} ({gewicht} kg) | <strong>Woche:</strong> {week}, Einheit {day} | <strong>Ziel:</strong> {day_label} | <strong>Phase:</strong> {PHASE_NAMES.get(effective_phase, effective_phase)} (vorgesehen: {PHASE_NAMES.get(planned_phase, planned_phase)}) | <strong>Lauf-ABC Last:</strong> {abc_last_str}</p>
    <p>{escape(test_note)}</p>
    <p>{escape(assignment_text)}</p>
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
    <td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"8–6–5 Wdh." if quality_day else rep_rule(geschlecht_wahl, level)}</td>
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
    <td style="padding: 6px 8px; border: 1px solid #D9D9D9;">{"5–8 Wdh." if quality_day else rep_rule(geschlecht_wahl, level)}</td>
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
    html_matrix = organize_multisport_html(html_matrix, einheiten, short_day, main_sets, "Fussball", band, org_config, timing, focus, block_rounds)
    return html_matrix

st.title('Doc Athletic Train Smart Evolution Software')
st.caption('Fußball 120 · '+BUILD_STAND)
auth_fingerprint = hashlib.sha256(json.dumps([TRAINER_CODE,GAST_CODE,DATABASE_URL]).encode()).hexdigest()
if st.session_state.get("auth_fingerprint") != auth_fingerprint:
    st.session_state.clear()
    st.session_state.auth_fingerprint = auth_fingerprint
if not TRAINER_CODE:
    st.info("Trainerzugang einrichten: In den Streamlit-Einstellungen unter Secrets den Eintrag DOC_ATHLETIC_TRAINER_CODE mit einem eigenen Zugangscode speichern. Danach die App neu laden.")
    st.stop()
if DATABASE_URL:
    st.caption("Speicher: externe PostgreSQL-Datenbank")
else:
    st.warning("Speicher lokal, nicht dauerhaft garantiert: Nach der Arbeit unter Datensicherung ein Backup herunterladen. Externe Datenbank noch einrichten.")
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
    st.session_state.navigations_status = 'Operativ'
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

# APP_ROUTING
navigation=[('Training','Operativ'),('Athleten','Athleten'),('Tests / Import','Testtabelle'),('Datensicherung','Backup')]
if st.session_state.auth_modus=='gast':
    navigation=[item for item in navigation if item[1] not in ('Testtabelle','Backup')]
nav_columns=st.columns(len(navigation)+1)
for column,(label,target) in zip(nav_columns,navigation):
    column.button(label,on_click=navigiere,args=(target,),key='nav_'+target)
if nav_columns[-1].button('ABMELDEN'):
    st.session_state.clear();st.rerun()
page=st.session_state.navigations_status
if page=='Athleten':render_athlete_editor()
elif page=='Testtabelle' and st.session_state.auth_modus=='trainer':render_test_table()
elif page=='Backup' and st.session_state.auth_modus=='trainer':render_backup()
else:render_training()
