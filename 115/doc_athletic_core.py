"""Gemeinsame Planungsfunktionen. Fachwerte aus Stand 115.3 unverändert übernommen.

Eine Zuordnung nach Trainer-Einschätzung ist keine Messung biologischen Alters.
Fehlende Zuordnungsregeln werden ausdrücklich nicht durch Lastannahmen ersetzt.
"""
from copy import deepcopy
import math
from datetime import date

AGE_BANDS = ("U11", "U13", "U15", "U17", "U20", "U23", "MASTER")
ASSIGNMENT_RULE = "2026-09-24"
DEVELOPMENT_STEPS = {
    "Spätentwickler (Retardiert)": -1,
    "Normalentwickler": 0,
    "Frühentwickler (Akzeleriert)": 1,
}


def calendar_band(age):
    """Bisherige Ganzjahresgrenzen; keine Schätzung eines biologischen Alters."""
    if type(age) not in (int, float) or not math.isfinite(age) or int(age) != age or not 9 <= age <= 40:
        raise ValueError("Alter muss zwischen 9 und 40 ganzen Jahren liegen.")
    for upper, band in ((10,"U11"),(12,"U13"),(14,"U15"),(16,"U17"),(19,"U20"),(22,"U23"),(40,"MASTER")):
        if age <= upper:
            return band


def training_assignment(band, development, veto_band=None):
    """Zuordnung von Planvorlagen nach Trainerregel, ohne zusätzliche Lastfaktoren."""
    if band not in AGE_BANDS or development not in DEVELOPMENT_STEPS:
        raise ValueError("Altersklasse oder Entwicklungsstatus unbekannt.")
    if veto_band is not None and veto_band not in AGE_BANDS:
        raise ValueError("Trainingsklasse für das Trainer-Veto unbekannt.")
    # Frank, 24.09.2026: U11 (9/10 Jahre) bleibt unabhängig vom Entwicklungsstatus U11.
    step = 0 if band == "U11" else DEVELOPMENT_STEPS[development]
    target = AGE_BANDS.index(band) + step
    recommended = AGE_BANDS[target] if 0 <= target < len(AGE_BANDS) else None
    return {"calendar":band, "recommended":recommended,
            "effective":veto_band or recommended or band,
            "veto":veto_band is not None,
            "blocked":recommended is None and veto_band is None}


def validate_assignment(record):
    """Altbestände bleiben lesbar; neue Metadaten müssen zum wirksamen Plan passen."""
    if "trainingszuordnung" not in record:
        if "kalenderklasse" in record and record["kalenderklasse"] not in AGE_BANDS:
            raise ValueError("Altersklasse in Stammdaten unbekannt.")
        return
    cfg = record["trainingszuordnung"]
    if not isinstance(cfg,dict) or set(cfg) != {"regel","veto_klasse","veto_notiz"} or cfg.get("regel") != ASSIGNMENT_RULE:
        raise ValueError("Ungültige Trainingszuordnung.")
    if not isinstance(cfg["veto_notiz"],str) or len(cfg["veto_notiz"]) > 4000:
        raise ValueError("Trainer-Notiz zur Zuordnung prüfen.")
    result = training_assignment(record.get("kalenderklasse"),record.get("reife"),cfg["veto_klasse"])
    if record.get("profil", "").split("_")[1:2] != [result["effective"]]:
        raise ValueError("Gespeicherte Trainingsklasse passt nicht zur Zuordnung.")

PARTNER_PAUSE = "Lohnende Pause durch Partnerwechsel"

ABC_115 = {
    "U11": ((10., 20., "0"), (10., 20., "0")),
    "U13": ((15., 25., "0"), (15., 25., "0")),
    "U15": ((20., 30., "2"), (20., 30., "2")),
    "U17": ((25., 40., "3"), (20., 35., "3")),
    "U20": ((30., 50., "3"), (25., 40., "3")),
    "U23": ((30., 60., "3–4"), (25., 45., "3")),
    "MASTER": ((30., 60., "3–4"), (25., 45., "3")),
}

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

def phase_exercise_label(kind,effective):
    if effective=='Grundlast':return {'front_squat':'Front Squat – Grundlast und Technik','kreuzheben':'Kreuzheben – Grundlast und Technik','anreiss':'Anreiß-Streckung – Grundlast und Technik'}[kind]
    return PHASE_EXERCISES[kind]+(' Jumps' if effective=='Jumps' else ' Sprünge')

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


def powerbag_load(band, gender, override=0):
    """Einzige aktive Tabelle aus 115.3; keine konkurrierende Vorberechnung."""
    if override > 0:
        return f"Powerbag {override:g} kg (individuelle Trainerfestlegung)"
    if band == "U11":
        return "Körpergewicht; keine Powerbag-Zusatzlast hinterlegt"
    ranges = {
        "U13": ("8–10", "8–12"),
        "U15": ("8–12", "12–15 kg; bei Bedarf z. B. 10"),
        "U17": ("8–10", "15"),
        "U20": ("8–12", "17"),
        "U23": ("10–15", "20"),
        "MASTER": ("10–15", "20"),
    }
    return "Powerbag " + ranges[band][0 if gender == "Weiblich" else 1] + " kg"
