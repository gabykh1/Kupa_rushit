# """
# Supermarket geo + sales simulator
# Outputs:
#   geolocation.csv: device_id, lat, lon, timestamp, accuracy_m, role, area
#   log_sales.csv:   sale_id, timestamp, customer_id, subtotal, tax, total, payment_method

# Run:
#   python kupa_rashit_funs.py || --start 2025-06-01 --end 2025-11-30 --out .

# """

import argparse
import math
import os
import random
import uuid
from datetime import datetime, timedelta, time
import pandas as pd

random.seed(7)

# -------------------------
# Polygon helpers
# -------------------------
def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1):
            inside = not inside
    return inside

def random_point_in_polygon(polygon, max_iter=1000):
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    for _ in range(max_iter):
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        if point_in_polygon((lat, lon), polygon):
            return (lat, lon)
    return ((min_lat + max_lat) / 2.0, (min_lon + max_lon) / 2.0)

# -------------------------
# PLACEHOLDER POLYGONS — replace with your own
# -------------------------
PARKING_POLYGON = [
    (31.877970, 34.738616),
    (31.877795, 34.739125),
    (31.878309, 34.739383),
    (31.878472, 34.738931),
    (31.877970, 34.738616),
]

SUPER_MARKET_POLYGON = [
    (31.879136, 34.739282),
    (31.877970, 34.738606),
    (31.877594, 34.739718),
    (31.878794, 34.740357),
    (31.879136, 34.739282),
]

CASH_REGISTERS_POLYGON = [
    (31.878869, 34.739347),
    (31.878890, 34.739310),
    (31.878688, 34.739193),
    (31.878667, 34.739239),
    (31.878762, 34.739285),
    (31.878869, 34.739347),
]

BUTCHERY_POLYGON = [
    (31.878888, 34.739959),
    (31.878800, 34.739908),
    (31.878740, 34.740107),
    (31.878822, 34.740128),
    (31.878888, 34.739959),
]

WAREHOUSE_POLYGON = [
    (31.878300, 34.739383),
    (31.877791, 34.739135),
    (31.877665, 34.739517),
    (31.878164, 34.739760),
    (31.878300, 34.739383),
]

HEAD_OFFICE_POLYGON = [
    (31.877656, 34.739512),
    (31.877599, 34.739713),
    (31.878085, 34.739977),
    (31.878155, 34.739770),
    (31.877656, 34.739512),
]



AREAS = {
    "parking": PARKING_POLYGON,
    "supermarket": SUPER_MARKET_POLYGON,
    "cash_registers": CASH_REGISTERS_POLYGON,
    "butchery": BUTCHERY_POLYGON,
    "warehouse": WAREHOUSE_POLYGON,
    "head_office": HEAD_OFFICE_POLYGON,
}

# -------------------------
# Opening hours (Mon=0..Sun=6); Closed Saturday (Sat=5)
# -------------------------
OPENING_RULES = {
    6: (time(7,30), time(21,0)),  # Sunday
    0: (time(7,30), time(21,0)),  # Monday
    1: (time(7,30), time(21,0)),  # Tuesday
    2: (time(7,30), time(22,0)),  # Wednesday
    3: (time(7,30), time(22,0)),  # Thursday
    4: (time(7,0),  time(15,0)),  # Friday
    # Saturday closed
}

HOLIDAYS = {
    datetime(2025, 6, 2).date(),   # Shavuot – supermarket closed
    datetime(2025, 9, 23).date(),  # Rosh Hashanah (Day 1)
    datetime(2025, 9, 24).date(),  # Rosh Hashanah (Day 2)
    datetime(2025,10,2).date(),    # Yom Kippur – supermarket closed
    datetime(2025,10,7).date(),    # Sukkot – supermarket closed
    datetime(2025,10,14).date(),   # Shemini Atzeret / Simchat Torah – closed
}

# Days with high activity, early closing, or exceptional behavior
SPECIAL_DAYS = {
    datetime(2025,6,1).date(),   # Shavuot Eve – big shopping spike, early close
    # 13–24 June war period spike → we'll list key days
    datetime(2025,6,13).date(),  # Friday – big spike, war preparation
    datetime(2025,6,14).date(),  # Saturday – exceptional opening
    # protest-related days
    datetime(2025,8,17).date(),  # National strike & protest – higher sales
    datetime(2025,8,26).date(),  # Solidarity disruptions day
    # holiday season peaks
    datetime(2025,9,22).date(),  # Rosh Hashanah Eve – strong spike
    datetime(2025,10,1).date(),  # Yom Kippur Eve – strong spike
    datetime(2025,10,6).date(),  # Sukkot Eve – strong spike
    datetime(2025,10,13).date(), # Eve of Simchat Torah – strong spike
}
# -------------------------
# Roles & staffing
# -------------------------
ROLE_CONFIG = {
    "manager": {"count": 1, "accuracy_m": (5, 39)},
    "cashier": {"count": 15, "accuracy_m": (1, 37)},
    "butcher": {"count": 4, "accuracy_m": (1, 43)},
    "delivery_guy": {"count": 8, "accuracy_m": (3, 20)},
    "general_worker": {"count": 10, "accuracy_m": (4, 12)},
    "senior_general_worker": {"count": 1, "accuracy_m": (4, 10)},
    "security_guy": {"count": 4, "accuracy_m": (15, 150)},
    "repeat_customer": {"count": 112, "accuracy_m": (4, 45)},
    "one_time_customer": {"count": 388, "accuracy_m": (2, 34)},
    "no_phone": {"count": 221, "accuracy_m": None},
    "not_paying": {"count": 176, "accuracy_m": (5, 36)},
}
# -------------------------
# slope - linear regression
# -------------------------
VAT_RATE = 0.18        
MAX_TOTAL_NIS = 1500.0 
# ---- Foot-traffic trend controls (very slight) ----
WEEKLY_DECAY_PCT     = 0.005   # ~0.5% fewer customers each new week 
WEEKLY_SHOCK_PCT     = 0.03    # ±3% weekly shock: some weeks a bit higher/lower
DAILY_NOISE_PCT      = 0.08    # ±2% day-to-day noise (tiny)

# Minimal weekday seasonality (Mon=0..Sun=6). Keep it subtle.
WEEKDAY_SEASONALITY = {
    0: 1.00,  # Mon
    1: 1.00,  # Tue
    2: 1.00,  # Wed
    3: 1.02,  # Thu (slightly busier)
    4: 1.04,  # Fri (short day but busy)
    5: 0.00,  # Sat (closed)
    6: 1.01,  # Sun (tiny bump)
}



def role_accuracy(role):
    rng = ROLE_CONFIG[role]["accuracy_m"]
    if rng is None:
        return 0.0
    lo, hi = rng
    return random.uniform(lo, hi) 

def make_ids(role, n):
    return [f"{role[:3]}_{i:03d}" for i in range(1, n+1)]

ID_POOLS = {r: make_ids(r, ROLE_CONFIG[r]["count"]) for r in ROLE_CONFIG}

# -------------------------
# Shift builders
# -------------------------
def dt(date_obj, t):
    return datetime.combine(date_obj, t)

def clamp_to_open_hours(date_obj, start_dt, end_dt):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return None
    open_t, close_t = OPENING_RULES[wd]
    day_open = dt(date_obj, open_t)
    day_close = dt(date_obj, close_t)
    start = max(day_open, start_dt)
    end = min(day_close, end_dt)
    if end <= start:
        return None
    return (start, end)

def manager_shift(date_obj):
    start = dt(date_obj, time(8, 0)) + timedelta(minutes=random.randint(-20, 30))
    end = dt(date_obj, time(17, 0)) + timedelta(minutes=random.randint(-30, 30))
    w = clamp_to_open_hours(date_obj, start, end)
    if not w:
        return []
    s, e = w
    segs, total = [], (e - s).seconds // 60
    tour_points = sorted(random.sample(range(60, max(61, total-60)), k=2)) if total > 120 else []
    last = s
    for tp in tour_points + [total]:
        mid = s + timedelta(minutes=tp)
        segs.append(("HEAD_OFFICE", last, mid))
        if tp != total:
            t_end = min(mid + timedelta(minutes=random.randint(10, 20)), e)
            segs.append(("SUPERMARKET", mid, t_end))
            last = t_end
    return segs

def cashier_shifts(date_obj):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return []
    open_t, close_t = OPENING_RULES[wd]
    base_start = dt(date_obj, open_t)
    base_end = dt(date_obj, close_t)
    windows = []
    shift_count = 3 if wd not in (3,4) else 4
    for _ in range(shift_count):
        dur_h = random.randint(6, 8)
        start = base_start + timedelta(hours=random.randint(0, 6))
        end = min(start + timedelta(hours=dur_h), base_end)
        w = clamp_to_open_hours(date_obj, start, end)
        if w:
            windows.append(("CASH_REGISTERS", w[0], w[1]))
    if wd == 3:
        w = clamp_to_open_hours(date_obj, dt(date_obj, time(16, 0)), dt(date_obj, time(20, 0)))
        if w: windows += [("CASH_REGISTERS", w[0], w[1])] * 2
    if wd == 4:
        w = clamp_to_open_hours(date_obj, dt(date_obj, time(8, 0)), dt(date_obj, time(14, 0)))
        if w: windows += [("CASH_REGISTERS", w[0], w[1])] * 2
    return windows

def butchery_shifts(date_obj):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return []
    if wd == 4: start, end = time(9,0), time(14,0)
    else:        start, end = time(10,0), time(19,0)
    w = clamp_to_open_hours(date_obj, dt(date_obj, start), dt(date_obj, end))
    return [("BUTCHERY", w[0], w[1]), ("BUTCHERY", w[0], w[1])] if w else []

def delivery_shifts(date_obj):
    wd = date_obj.weekday()
    if wd in (0, 3) and date_obj not in HOLIDAYS:
        start = dt(date_obj, time(6, 0)) + timedelta(minutes=random.randint(-10, 10))
        end = start + timedelta(minutes=30)
        return [("WAREHOUSE", start, end)]
    return []

def general_worker_shifts(date_obj):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return []
    end_h = 20 if wd in (6,0,1,2) else (22 if wd==3 else 15)
    w = clamp_to_open_hours(date_obj, dt(date_obj, time(8,0)), dt(date_obj, time(end_h,0)))
    return [("SUPERMARKET", w[0], w[1])] if w else []

def senior_general_shift(date_obj):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return []
    start = dt(date_obj, time(6, 0 if wd in (0,3) else 30))
    end = dt(date_obj, time(20,0))
    w = clamp_to_open_hours(date_obj, start, end)
    return [("SUPERMARKET", w[0], w[1])] if w else []

def security_shift(date_obj):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS:
        return []
    open_t, close_t = OPENING_RULES[wd]
    return [("PARKING", dt(date_obj, open_t), dt(date_obj, close_t))]

# -------------------------
# Customers
# -------------------------
def plan_customer_trip(date_obj, is_repeat=False, no_phone=False, not_paying=False, special=False):
    wd = date_obj.weekday()
    if wd == 5 or date_obj in HOLIDAYS: return []
    open_t, close_t = OPENING_RULES[wd]
    open_dt, close_dt = dt(date_obj, open_t), dt(date_obj, close_t)
    if wd == 3:
        base_arr = dt(date_obj, time(random.choice([10,12,16,18]), random.randint(0,59)))
    elif wd == 4:
        base_arr = dt(date_obj, time(random.choice([8,9,11,12,13]), random.randint(0,59)))
    else:
        base_arr = dt(date_obj, time(random.choice([9,11,13,17]), random.randint(0,59)))
    base_arr = max(base_arr, open_dt + timedelta(minutes=random.randint(0, 60)))
    dwell = random.randint(10, 90)
    if is_repeat and wd in (3,4): dwell += random.randint(15,45)
    if special: dwell += random.randint(5,20)
    leave = min(base_arr + timedelta(minutes=dwell), close_dt - timedelta(minutes=1))
    segs = []
    if random.random() < 0.8:
        p_end = base_arr + timedelta(minutes=random.randint(2,10))
        segs.append(("PARKING", base_arr, p_end))
        start_market = p_end
    else:
        start_market = base_arr
    roam_end = min(leave - timedelta(minutes=1), start_market + timedelta(minutes=max(3, dwell-3)))
    if roam_end > start_market:
        segs.append(("SUPERMARKET", start_market, roam_end))
    if (not not_paying) and (not no_phone):
        pay_start = roam_end
        pay_end = min(leave, pay_start + timedelta(minutes=random.randint(2,10)))
        if pay_end > pay_start:
            segs.append(("CASH_REGISTERS", pay_start, pay_end))
    return segs

def emit_points_for_segment(device_id, role, area_key, start_dt, end_dt, detect_prob=0.4):
    polygon = AREAS[area_key.lower()]
    ts = start_dt
    rows = []
    while ts <= end_dt:
        if random.random() < detect_prob:
            lat, lon = random_point_in_polygon(polygon)
            rows.append({
                "device_id": device_id,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "timestamp": ts.isoformat(),
                "accuracy_m": round(role_accuracy(role), 1),
                "role": role,
                "area": area_key
            })
        ts += timedelta(minutes=1)
    return rows

PAYMENT_METHODS = ["cash", "credit_card", "debit_card", "mobile_pay"]

def purchase_amount_from_dwell(dwell_minutes):
    base = random.uniform(10, 30)
    slope = random.uniform(4, 9)  # per minute
    expected = base + slope * dwell_minutes
    noise = random.uniform(-0.1, 0.1) * expected
    amt = expected + noise

    max_subtotal = MAX_TOTAL_NIS / (1.0 + VAT_RATE)
    return max(5.0, min(amt, max_subtotal))

def build_sale(customer_id, ts, dwell_minutes, is_no_phone=False):
    
    if dwell_minutes is None:
        subtotal = round(random.uniform(20, 460), 2) # no phone
    else:
        subtotal = round(purchase_amount_from_dwell(dwell_minutes), 2)

    tax = round(subtotal * VAT_RATE, 2)
    total = round(subtotal + tax, 2)

    if total > 300:
        payment_method = random.choice(["credit_card", "debit_card"])
    else:
        payment_method = random.choice(PAYMENT_METHODS)

    return {
        "sale_id": str(uuid.uuid4())[:8],
        "timestamp": ts.isoformat(),
        "customer_id": None if is_no_phone else customer_id,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "payment_method": payment_method,
        "dwell_minutes": None if is_no_phone else int(dwell_minutes),
    }


def sunday_of(date_obj):
    """Return the Sunday (week start) for the given date (Sun..Sat week)."""
    # In Python, Monday=0..Sunday=6. For Sun-start week:
    # offset = (weekday + 1) % 7
    return date_obj - timedelta(days=(date_obj.weekday() + 1) % 7)

def build_week_shocks(start_date_obj, end_date_obj):
    """Create a dict: {week_start_sunday: shock_factor}, one per week in range."""
    shocks = {}
    first_week = sunday_of(start_date_obj)
    d = first_week
    while d <= end_date_obj:
        # shock factor in [1-3%, 1+3%]
        shocks[d] = 1.0 + random.uniform(-WEEKLY_SHOCK_PCT, WEEKLY_SHOCK_PCT)
        d += timedelta(days=7)
    return shocks

def traffic_scale_for_date(date_obj, first_week_start, week_shocks):
    """
    Very slight weekly decay + weekly shock + tiny daily noise + subtle weekday seasonality.
    Sunday starts a new 'week index'.
    """
    this_week_start = sunday_of(date_obj)
    week_index = (this_week_start - first_week_start).days // 7  # 0,1,2,...

    # Exponential weekly decay (very slight)
    week_decay = (1.0 - WEEKLY_DECAY_PCT) ** week_index

    # Weekly shock (some weeks a bit higher/lower)
    shock = week_shocks.get(this_week_start, 1.0)

    # Tiny daily noise
    daily = 1.0 + random.uniform(-DAILY_NOISE_PCT, DAILY_NOISE_PCT)

    # Subtle weekday seasonality
    season = WEEKDAY_SEASONALITY.get(date_obj.weekday(), 1.0)

    return week_decay * shock * daily * season


def generate_data(start_date, end_date, out_dir):
    # Ensure output dir exists
    os.makedirs(out_dir, exist_ok=True)

    georows, sales = [], []

    def pick_ids(role, k):
        pool = ID_POOLS[role]
        k = min(k, len(pool))
        return random.sample(pool, k)

    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    first_week_start = sunday_of(start)
    WEEK_SHOCKS = build_week_shocks(start, end)


    repeat_ids = pick_ids("repeat_customer", 100)

    d = start
    while d <= end:
        special = d in SPECIAL_DAYS
        wd = d.weekday()
        if d in HOLIDAYS or wd == 5:
            d += timedelta(days=1)
            continue
        scale = traffic_scale_for_date(d, first_week_start, WEEK_SHOCKS)


        # Workers
        for area, s, e in manager_shift(d):
            georows += emit_points_for_segment(ID_POOLS["manager"][0], "manager", area, s, e)

        cashier_windows = cashier_shifts(d)
        for cid, (area, s, e) in zip(pick_ids("cashier", len(cashier_windows)), cashier_windows):
            georows += emit_points_for_segment(cid, "cashier", area, s, e)

        butch_windows = butchery_shifts(d)
        for bid, (area, s, e) in zip(pick_ids("butcher", len(butch_windows)), butch_windows):
            georows += emit_points_for_segment(bid, "butcher", area, s, e)

        for (area, s, e) in delivery_shifts(d):
            for did in pick_ids("delivery_guy", 2):
                georows += emit_points_for_segment(did, "delivery_guy", area, s, e)

        for (area, s, e) in general_worker_shifts(d):
            for gid in pick_ids("general_worker", 2):
                georows += emit_points_for_segment(gid, "general_worker", area, s, e)

        for (area, s, e) in senior_general_shift(d):
            georows += emit_points_for_segment(ID_POOLS["senior_general_worker"][0], "senior_general_worker", area, s, e)

        for (area, s, e) in security_shift(d):
            sid = random.choice(ID_POOLS["security_guy"])
            georows += emit_points_for_segment(sid, "security_guy", area, s, e)

        # Customers
        todays_repeat = []

        # Base probabilities
        p_weekendish = 0.70  # Thu/Fri
        p_weekday    = 0.35  # Sun/Mon/Tue/Wed

        # Apply scale and clamp between 0–1
        p_weekendish = min(1.0, max(0.0, p_weekendish * scale))
        p_weekday    = min(1.0, max(0.0, p_weekday * scale))

        for rid in repeat_ids:
            go_today = (wd in (3,4) and random.random() < p_weekendish) or \
                       (wd in (6,0,1,2) and random.random() < p_weekday)
            if special and not go_today and random.random() < 0.15:
                go_today = True
            if go_today:
                todays_repeat.append(rid)

        one_time_count = random.randint(3,7)
        np_count       = random.randint(10,35)
        nophone_count  = random.randint(15,25)

        # Apply scale and round gently (never negative)
        one_time_count = max(0, int(round(one_time_count * scale)))
        np_count       = max(0, int(round(np_count * scale)))
        nophone_count  = max(0, int(round(nophone_count * scale)))

        if special:
            one_time_count = int(math.ceil(one_time_count * 1.3))
            np_count       = int(math.ceil(np_count * 1.3))
            nophone_count  = int(math.ceil(nophone_count * 1.3))

        todays_one_time = pick_ids("one_time_customer", one_time_count)
        todays_np       = pick_ids("not_paying", np_count)
        todays_nophone  = pick_ids("no_phone", nophone_count)


        for cust_id in todays_repeat + todays_one_time + todays_np:
            role = "repeat_customer" if cust_id in todays_repeat else ("not_paying" if cust_id in todays_np else "one_time_customer")
            segs = plan_customer_trip(d, is_repeat=(role=="repeat_customer"), not_paying=(role=="not_paying"), special=special)
            if not segs: continue
            for (area, s, e) in segs:
                georows += emit_points_for_segment(cust_id, role, area, s, e)
            if role != "not_paying":
                regs = [(s,e) for (a,s,e) in segs if a=="CASH_REGISTERS"]
                if regs:
                    s,e = regs[-1]
                    dwell = sum(int((e2-s2).total_seconds()//60) for (a2,s2,e2) in segs if a2!="PARKING")
                    sales.append(build_sale(cust_id, e, dwell))

        for cust_id in todays_nophone:
            segs = plan_customer_trip(d, no_phone=True, special=special)
            if segs:
                regs = [(s,e) for (a,s,e) in segs if a=="CASH_REGISTERS"]
                if regs:
                    s,e = regs[-1]
                    dwell = sum(int((e2-s2).total_seconds()//60) for (a2,s2,e2) in segs if a2!="PARKING")
                    sales.append(build_sale(cust_id, e, dwell_minutes=None, is_no_phone=True))
                else:
                    _, _, last_end = segs[-1]
                    sales.append(build_sale(customer_id=None, ts=last_end, dwell_minutes=None, is_no_phone=True))


        d += timedelta(days=1)

    geo_df = pd.DataFrame(georows, columns=["device_id", "lat", "lon", "timestamp", "accuracy_m", "role", "area"])
    sales_df = pd.DataFrame(sales, columns=["sale_id", "timestamp", "customer_id", "subtotal", "tax", "total", "payment_method", "dwell_minutes"])

    geo_path = os.path.join(out_dir, "geolocation.csv")
    sales_path = os.path.join(out_dir, "log_sales.csv")
    geo_df.to_csv(geo_path, index=False, encoding="utf-8")
    sales_df.to_csv(sales_path, index=False, encoding="utf-8")

    print(f"[OK] Wrote {len(geo_df):,} rows → {geo_path}")
    print(f"[OK] Wrote {len(sales_df):,} rows → {sales_path}")

# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2025-06-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end",   default="2025-11-30", help="End date YYYY-MM-DD")
    parser.add_argument("--out",   default=".", help="Output directory (default: current folder)")
    args = parser.parse_args()

    generate_data(args.start, args.end, args.out)

