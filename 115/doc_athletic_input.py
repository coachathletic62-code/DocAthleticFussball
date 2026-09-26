"""Textbasierte Zahleneingabe für Tippen und Betriebssystem-Diktat.

Kein Audio wird durch die App aufgenommen oder an einen KI-Dienst geschickt.
Die Tastatur des Endgeräts liefert bereits transkribierten Text.
"""
from decimal import Decimal, InvalidOperation
import math
import re
import unicodedata

SMALL_NUMBERS = {
    'null':0, 'ein':1, 'eins':1, 'eine':1, 'zwei':2, 'drei':3, 'vier':4,
    'fünf':5, 'sechs':6, 'sieben':7, 'acht':8, 'neun':9, 'zehn':10,
    'elf':11, 'zwölf':12, 'dreizehn':13, 'vierzehn':14, 'fünfzehn':15,
    'sechzehn':16, 'siebzehn':17, 'achtzehn':18, 'neunzehn':19,
    'zwanzig':20, 'dreißig':30, 'vierzig':40, 'fünfzig':50,
    'sechzig':60, 'siebzig':70, 'achtzig':80, 'neunzig':90,
}


def _integer_word(text):
    text=text.strip()
    if text.isdigit():
        return int(text)
    if any(char.isdigit() for char in text):
        raise ValueError('Bitte eine einzelne eindeutige Zahl eingeben.')
    text=text.replace(' ', '').replace('-', '')
    if text in SMALL_NUMBERS:
        return SMALL_NUMBERS[text]
    if 'hundert' in text:
        left,right=text.split('hundert',1)
        hundreds=1 if not left else _integer_word(left)
        if not 1<=hundreds<=9:
            raise ValueError('Zahlwort nicht eindeutig.')
        return hundreds*100+(_integer_word(right) if right else 0)
    if 'und' in text:
        left,right=text.split('und',1)
        if left in SMALL_NUMBERS and right in SMALL_NUMBERS and 1<=SMALL_NUMBERS[left]<=9 and SMALL_NUMBERS[right] in range(20,100,10):
            return SMALL_NUMBERS[left]+SMALL_NUMBERS[right]
    raise ValueError('Bitte eine einzelne eindeutige Zahl eingeben.')


def parse_number(text, minimum=None, maximum=None, integer=False, allow_empty=False):
    raw=unicodedata.normalize('NFKC',str(text)).strip().casefold()
    if not raw:
        if allow_empty:
            return None
        raise ValueError('Bitte einen Wert eingeben.')
    # Einheiten werden nicht stillschweigend umgerechnet.
    if ',' in raw and '.' in raw:
        raise ValueError('Bitte ohne Tausendertrennzeichen eingeben.')
    raw=re.sub(r'\bkomma\b', ',',raw)
    raw=re.sub(r'\bpunkt\b', '.',raw)
    sign=-1 if raw.startswith('minus ') or raw.startswith('-') else 1
    raw=re.sub(r'^(minus\s+|-)', '',raw).strip()
    if re.fullmatch(r'\d+(?:[,.]\d+)?',raw):
        normalized=raw.replace(',','.')
    else:
        pieces=re.split(r'[,\.]',raw)
        if len(pieces)>2:
            raise ValueError('Bitte eine einzelne eindeutige Zahl eingeben.')
        whole=_integer_word(pieces[0])
        normalized=str(whole)
        if len(pieces)==2:
            fractional=pieces[1].strip()
            words=fractional.split()
            if not fractional:
                raise ValueError('Nachkommastellen fehlen.')
            if len(words)>1 and all(w in SMALL_NUMBERS and SMALL_NUMBERS[w]<10 for w in words):
                digits=''.join(str(SMALL_NUMBERS[w]) for w in words)
            elif fractional.isdigit():
                digits=fractional
            else:
                digits=str(_integer_word(fractional))
            normalized+='.'+digits
    try:
        value=Decimal(normalized)*sign
    except InvalidOperation as exc:
        raise ValueError('Zahl nicht lesbar.') from exc
    if not value.is_finite():
        raise ValueError('Eine endliche Zahl ist erforderlich.')
    if integer and value!=value.to_integral_value():
        raise ValueError('Bitte eine ganze Zahl eingeben.')
    if minimum is not None and value<Decimal(str(minimum)):
        raise ValueError(f'Mindestens {minimum:g} eingeben.')
    if maximum is not None and value>Decimal(str(maximum)):
        raise ValueError(f'Höchstens {maximum:g} eingeben.')
    result=int(value) if integer else float(value)
    if not math.isfinite(result):
        raise ValueError('Zahl liegt außerhalb des darstellbaren Bereichs.')
    return result


def voice_number_input(label, min_value=None, max_value=None, value='min', step=None,
                       format=None, key=None, help=None, disabled=False, container=None,
                       validation_errors=None, **kwargs):
    import streamlit as st
    target=container if container is not None else st
    if value=='min':
        value=min_value if min_value is not None else 0
    integer=(type(value) is int) or (value is None and type(min_value) is int and (step is None or type(step) is int))
    initial='' if value is None else (str(value) if integer else f'{Decimal(str(value)):f}')
    if '.' in initial:
        initial=initial.rstrip('0').rstrip('.')
    initial=initial.replace('.',',')
    text_key='zahl_'+str(key) if key is not None else None
    raw=target.text_input(label, value=initial, key=text_key, help=help,
                          disabled=disabled, **{k:v for k,v in kwargs.items() if k in ('label_visibility','placeholder','width')})
    try:
        return parse_number(raw,min_value,max_value,integer,allow_empty=value is None)
    except ValueError as exc:
        message=f'{label}: {exc}'
        target.error(message)
        if validation_errors is not None:
            # Forms must render their submit button even after invalid input.
            # The caller rejects the submission if this list is nonempty.
            validation_errors.append(message)
            return None
        st.stop()
