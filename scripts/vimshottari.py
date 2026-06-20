#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Калькулятор Вимшоттари-даш (чистый Python, без зависимостей).

Считает таймлайн махадаш и антардаш из сидерической долготы Луны на момент
рождения. Детерминированный — эфемериды не нужны.

Значения по умолчанию — для Ксении (Луна Лев 24°29'08" сидерически, Lahiri).
Если данные рождения меняются — поправь BIRTH/MOON_LON и перегенерируй:

    python3 vimshottari.py > ../data/dasha.md
"""

from datetime import datetime, timedelta

# --- Данные рождения --------------------------------------------------------
BIRTH = datetime(1991, 11, 2, 12, 30)              # местное время
MOON_LON = 120 + 24 + 29 / 60 + 8 / 3600           # Лев 24°29'08" = 144.4856°
YEAR_DAYS = 365.25                                  # длина года в днях

# Порядок и длительность периодов Вимшоттари (годы), сумма = 120
LORDS = [
    ("Кету", 7), ("Венера", 20), ("Солнце", 6), ("Луна", 10),
    ("Марс", 7), ("Раху", 18), ("Юпитер", 16), ("Сатурн", 19),
    ("Меркурий", 17),
]
TOTAL = 120
NAK_SPAN = 360 / 27                                 # 13°20' = 13.3333°
NAKSHATRA = "Пурвапхалгуни"                         # для справки в шапке


def add_years(dt, years):
    return dt + timedelta(days=years * YEAR_DAYS)


def fmt(dt):
    return dt.strftime("%d.%m.%Y")


def antardashas(md_lord_idx, md_start, md_years):
    """Антардаши (бхукти) внутри полной махадаши."""
    rows, cursor = [], md_start
    for j in range(9):
        name, full = LORDS[(md_lord_idx + j) % 9]
        sub_years = md_years * full / TOTAL
        end = add_years(cursor, sub_years)
        rows.append((name, cursor, end))
        cursor = end
    return rows


# --- Стартовая махадаша и баланс на рождение --------------------------------
nak_index = int(MOON_LON // NAK_SPAN)               # 0-based номер накшатры
pos_in_nak = MOON_LON - nak_index * NAK_SPAN
frac_elapsed = pos_in_nak / NAK_SPAN
start_idx = nak_index % 9
start_years = LORDS[start_idx][1]
balance = (1 - frac_elapsed) * start_years

# --- Список махадаш ---------------------------------------------------------
mds, cursor = [], BIRTH
name, full = LORDS[start_idx]
end = add_years(cursor, balance)
mds.append([name, cursor, end, balance, True])      # первая — частичная
cursor = end
for k in range(1, 9):
    name, full = LORDS[(start_idx + k) % 9]
    end = add_years(cursor, full)
    mds.append([name, cursor, end, full, False])
    cursor = end

# --- Вывод markdown ---------------------------------------------------------
out = []
out.append("# Вимшоттари-даши (планетные периоды)")
out.append("")
out.append("**Вимшоттари-даша** — система планетных периодов джйотиша: вся жизнь "
           "поделена на большие отрезки-**махадаши**, каждым «правит» одна планета; "
           "внутри — подпериоды-**антардаши** (бхукти). Показывает, какая планета "
           "«у руля» в конкретный отрезок жизни.")
out.append("")
out.append(f"Рассчитано детерминированно от долготы Луны "
           f"(накшатра {NAKSHATRA}, баланс на рождение — "
           f"{balance:.2f} года периода {LORDS[start_idx][0]}). "
           f"Длина года — {YEAR_DAYS} дн.")
out.append("")
out.append("> Чтобы понять текущий период — сравни сегодняшнюю дату с таблицей "
           "махадаш, затем с антардашами внутри неё.")
out.append("")
out.append("## Махадаши (большие периоды)")
out.append("")
out.append("| Период (планета) | Начало | Конец | Длительность |")
out.append("|---|---|---|---|")
for name, s, e, length, partial in mds:
    tag = " (остаток с рождения)" if partial else ""
    out.append(f"| {name}{tag} | {fmt(s)} | {fmt(e)} | {length:.2f} г |")
out.append("")
out.append("## Антардаши (подпериоды) внутри каждой полной махадаши")
out.append("")
out.append("_Первая махадаша частичная (началась до рождения), её антардаши "
           "опущены — это раннее детство._")
out.append("")
for name, s, e, length, partial in mds:
    if partial:
        continue
    md_idx = next(i for i, l in enumerate(LORDS) if l[0] == name)
    out.append(f"### Махадаша {name} ({fmt(s)} – {fmt(e)})")
    out.append("")
    out.append("| Антардаша | Начало | Конец |")
    out.append("|---|---|---|")
    for sub, ss, se in antardashas(md_idx, s, length):
        out.append(f"| {name}–{sub} | {fmt(ss)} | {fmt(se)} |")
    out.append("")

print("\n".join(out))
