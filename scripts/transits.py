#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Калькулятор транзитов (текущего неба) на Swiss Ephemeris.

Считает СЫРЫЕ положения планет на заданную дату (по умолчанию — сегодня)
в обеих системах и сопоставляет с натальной картой Ксении:
  - Западные (тропические) позиции, аспекты к наталу, дом Плацидус
  - Ведические (сидерические, Lahiri) позиции, дом от Лагны и от Луны

Скрипт выдаёт только астрономию. Вся интерпретация — на стороне скилла.

Запуск:
    python3 transits.py            # на сегодня
    python3 transits.py 2025-09-01 # на конкретную дату (для ретро/электива)

Если pyswisseph не установлен — печатает уведомление, чтобы скилл взял
данные из веба.
"""
import sys
from datetime import datetime, timezone

try:
    import swisseph as swe
except ImportError:
    print("EPHEMERIS_UNAVAILABLE: модуль pyswisseph не установлен.")
    print("Возьми текущие тропические положения из веба; для джйотиша вычти "
          "аянамшу Lahiri (~24°13′ на 2026 год, растёт ~50.3″/год).")
    sys.exit(0)

SIGNS = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы",
         "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
NAKS = ["Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира", "Ардра",
        "Пунарвасу", "Пушья", "Ашлеша", "Магха", "Пурвапхалгуни",
        "Уттарапхалгуни", "Хаста", "Читра", "Свати", "Вишакха", "Анурадха",
        "Джйештха", "Мула", "Пурвашадха", "Уттарашадха", "Шравана",
        "Дхаништха", "Шатабхиша", "Пурвабхадрапада", "Уттарабхадрапада",
        "Ревати"]

# --- Натал: западные тропические долготы (для аспектов и домов) -------------
NATAL_TROP = {
    "Солнце": 219.376, "Луна": 168.233, "Меркурий": 236.967,
    "Венера": 172.862, "Марс": 221.268, "Юпитер": 159.659,
    "Сатурн": 300.853, "Уран": 280.641, "Нептун": 284.365,
    "Плутон": 229.856, "ASC": 290.494, "MC": 225.261, "Раху": 282.101,
}
# Куспиды домов Плацидус (тропик)
CUSPS = [290.494, 335.306, 15.886, 45.261, 67.795, 88.072,
         110.494, 155.306, 195.886, 225.261, 247.795, 268.072]

# --- Натал: ведические сидерические долготы (Lahiri) ------------------------
NATAL_SID = {
    "Солнце": 195.617, "Луна": 144.486, "Меркурий": 213.217,
    "Венера": 149.100, "Марс": 197.517, "Юпитер": 135.900,
    "Сатурн": 277.100, "Раху": 258.350, "Кету": 78.350,
}
LAGNA_SIGN = 8   # Стрелец (Овен=0)
MOON_SIGN = 4    # Лев

PLANETS = [("Солнце", swe.SUN), ("Луна", swe.MOON), ("Меркурий", swe.MERCURY),
           ("Венера", swe.VENUS), ("Марс", swe.MARS), ("Юпитер", swe.JUPITER),
           ("Сатурн", swe.SATURN), ("Уран", swe.URANUS),
           ("Нептун", swe.NEPTUNE), ("Плутон", swe.PLUTO)]

ASPECTS = {0: "соединение", 60: "секстиль", 90: "квадрат",
           120: "тригон", 180: "оппозиция"}
ORB = 3.0


def dms(lon):
    d = int(lon % 30)
    m = int(round((lon % 30 - d) * 60))
    return f"{d}°{m:02d}′"


def sign_of(lon):
    return SIGNS[int(lon // 30)]


def nak_of(lon):
    return NAKS[int(lon // (360 / 27))]


def house_placidus(lon):
    for i in range(12):
        a, b = CUSPS[i], CUSPS[(i + 1) % 12]
        if a < b:
            if a <= lon < b:
                return i + 1
        else:  # wrap через 0°
            if lon >= a or lon < b:
                return i + 1
    return None


def house_whole(sign_idx, ref_sign):
    return ((sign_idx - ref_sign) % 12) + 1


def get_jd(arg):
    if arg:
        dt = datetime.strptime(arg, "%Y-%m-%d")
        h = 12.0  # без времени берём полдень UT
    else:
        dt = datetime.now(timezone.utc)
        h = dt.hour + dt.minute / 60
    return swe.julday(dt.year, dt.month, dt.day, h), dt.strftime("%d.%m.%Y")


jd, datestr = get_jd(sys.argv[1] if len(sys.argv) > 1 else None)
out = [f"# Транзиты на {datestr}", ""]

# --- Западные (тропические) -------------------------------------------------
out.append("## Западные позиции (тропик) и аспекты к наталу")
out.append("")
out.append("| Планета | Знак | Градус | Дом (Плацидус) | Ретро |")
out.append("|---|---|---|---|---|")
trop = {}
for name, pid in PLANETS:
    lon, _ = swe.calc_ut(jd, pid)
    lon, speed = lon[0], lon[3]
    trop[name] = lon
    retro = "R" if speed < 0 else "—"
    out.append(f"| {name} | {sign_of(lon)} | {dms(lon)} | "
               f"{house_placidus(lon)} | {retro} |")
out.append("")
out.append("**Аспекты транзитных планет к натальным точкам (орб ≤ 3°):**")
out.append("")
hits = []
for tname, tlon in trop.items():
    for nname, nlon in NATAL_TROP.items():
        sep = abs((tlon - nlon + 180) % 360 - 180)
        for ang, label in ASPECTS.items():
            orb = abs(sep - ang)
            if orb <= ORB:
                hits.append(f"- транзитный {tname} {label} натальн. {nname} "
                            f"(орб {orb:.1f}°)")
out += hits if hits else ["- нет тесных аспектов в пределах орба"]
out.append("")

# --- Ведические (сидерические Lahiri) ---------------------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)
out.append("## Ведические позиции (сидерика, Lahiri)")
out.append("")
out.append("Дома: целознаковые. Л — дом от Лагны (Стрелец), Ч — дом от Луны (Лев).")
out.append("")
out.append("| Граха | Знак | Градус | Накшатра | Дом Л | Дом Ч | Ретро |")
out.append("|---|---|---|---|---|---|---|")
sid = {}
for name, pid in PLANETS:
    res, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
    lon, speed = res[0], res[3]
    sid[name] = lon
    si = int(lon // 30)
    retro = "R" if speed < 0 else "—"
    out.append(f"| {name} | {sign_of(lon)} | {dms(lon)} | {nak_of(lon)} | "
               f"{house_whole(si, LAGNA_SIGN)} | {house_whole(si, MOON_SIGN)} | {retro} |")
# Раху/Кету
node, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
rahu = node[0]
ketu = (rahu + 180) % 360
for name, lon in (("Раху", rahu), ("Кету", ketu)):
    si = int(lon // 30)
    out.append(f"| {name} | {sign_of(lon)} | {dms(lon)} | {nak_of(lon)} | "
               f"{house_whole(si, LAGNA_SIGN)} | {house_whole(si, MOON_SIGN)} | R |")
out.append("")
out.append("**Соединения с натальными грахами (орб ≤ 5°):**")
out.append("")
conj = []
allsid = dict(sid); allsid["Раху"] = rahu; allsid["Кету"] = ketu
for tname, tlon in allsid.items():
    for nname, nlon in NATAL_SID.items():
        sep = abs((tlon - nlon + 180) % 360 - 180)
        if sep <= 5:
            conj.append(f"- транзитный {tname} на натальном {nname} (орб {sep:.1f}°)")
out += conj if conj else ["- нет тесных соединений"]
out.append("")
# Сатурн от Луны — для Сад-Сати
sat_si = int(sid["Сатурн"] // 30)
h_from_moon = house_whole(sat_si, MOON_SIGN)
note = {12: "12-й от Луны — начало Сад-Сати", 1: "над Луной — пик Сад-Сати",
        2: "2-й от Луны — завершение Сад-Сати",
        4: "4-й от Луны — Малая Дхайя", 8: "8-й от Луны — Малая Дхайя"}.get(h_from_moon)
if note:
    out.append(f"**Транзит Сатурна:** {note}.")
    out.append("")

print("\n".join(out))
