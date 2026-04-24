"""
Live Schumann resonance modulator dla qsim.
Źródła: NOAA Kp (geomagnetyzm) + open-meteo (pogoda lokalna) + model jonosfery.

f_Schumann(t, lon) = f_base + df_daily(t, lon) + df_kp(Kp)
sigma_mod = f(Kp, pogoda_lokalna)

Pogoda: burza lokalna = źródło Schumanna → sigma_mod wyższy.
Offline-safe: każde źródło ma niezależny fallback.
"""

import math
import datetime
import urllib.request
import json

DEFAULT_LAT = 50.3   # Gliwice
DEFAULT_LON = 18.7

F_BASE = 7.83        # Hz — empiryczny fundament
F_MARS = 14.7        # Hz — Mars

# WMO weather codes → Schumann weather_mod
# Burza lokalna = źródło Schumanna → większa amplituda pola
_WEATHER_MOD = {
    range(0, 4):    (1.00, 'clear'),          # bezchmurnie / pochmurnie
    range(45, 50):  (1.02, 'fog'),            # mgła
    range(51, 68):  (1.03, 'drizzle/rain'),   # mżawka / deszcz
    range(71, 78):  (1.01, 'snow'),           # śnieg
    range(80, 83):  (1.04, 'showers'),        # przelotne opady
    range(95, 100): (1.15, 'thunderstorm'),   # BURZA — lokalne źródło Schumanna
}

def _weather_code_to_mod(code: int) -> tuple[float, str]:
    for r, (mod, label) in _WEATHER_MOD.items():
        if code in r:
            return mod, label
    return 1.01, 'overcast'


def _fetch_kp() -> tuple[float, str]:
    """NOAA Kp. Fallback offline: Kp=2.0."""
    try:
        url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
        r = urllib.request.urlopen(url, timeout=4)
        return float(json.loads(r.read())[-1]['Kp']), 'live'
    except OSError:
        return 2.0, 'offline'
    except Exception:
        return 2.0, 'offline'


def _fetch_weather(lat: float, lon: float) -> tuple[int, str]:
    """
    open-meteo current weathercode. Offline-safe: fallback code=0 (clear).
    Nie wymaga klucza API.
    """
    try:
        url = (
            f'https://api.open-meteo.com/v1/forecast'
            f'?latitude={lat}&longitude={lon}'
            f'&current=weathercode'
            f'&forecast_days=1'
        )
        r = urllib.request.urlopen(url, timeout=4)
        code = int(json.loads(r.read())['current']['weathercode'])
        return code, 'live'
    except OSError:
        return 0, 'offline'
    except Exception:
        return 0, 'offline'


def _df_daily(utc_hour: float, lon_deg: float) -> float:
    """Dzienna modulacja jonosfery ±0.5 Hz. Max w lokalnym południu."""
    local_hour = (utc_hour + lon_deg / 15.0) % 24
    return 0.5 * math.cos(2 * math.pi * (local_hour - 12) / 24)


def _df_kp(kp: float) -> float:
    """Kp → perturbacja f. Burza geomagnetyczna obniża f."""
    if kp <= 3:
        return -0.03 * kp
    return -0.09 - 0.1 * (kp - 3)


def get_schumann(lat: float | None = None,
                 lon: float | None = None,
                 utc_offset_h: float | None = None,
                 location_level: int = 1,
                 live: bool = True) -> dict:
    """
    Aktualny stan pola Schumanna z uwzględnieniem pogody.

    location_level (opt-in):
      0 — brak lokalizacji, tylko utc_offset_h (max prywatność, brak pogody)
      1 — strefa magnetyczna ('E'/'M'/'P') domyślnie M (Polska), pogoda dla strefy
      2 — pełne lat/lon (np. Gliwice), pogoda lokalna

    Jeśli lat/lon podane → level=2 automatycznie.
    Jeśli tylko utc_offset_h → level=0.
    """
    # Ustal level automatycznie jeśli niespójność
    if lat is not None and lon is not None:
        effective_level = 2
    elif utc_offset_h is not None and (lat is None):
        effective_level = 0
    else:
        effective_level = location_level

    now = datetime.datetime.now(datetime.timezone.utc)
    utc_hour = now.hour + now.minute / 60

    # Wyprowadź lon do modelu dziennego
    if effective_level == 0:
        # Tylko strefa czasowa — udawaj lon = offset*15
        offset = utc_offset_h if utc_offset_h is not None else 2.0
        lon_model = offset * 15.0
        lat_used = None
    elif effective_level == 1:
        # Strefa magnetyczna — Polska = M (mid-latitude)
        # średnia CEST lon~15°, lat_band = 'M' (30-60°)
        lon_model = 15.0
        lat_used = None
    else:
        lon_model = lon if lon is not None else DEFAULT_LON
        lat_used = lat if lat is not None else DEFAULT_LAT

    if live:
        kp, kp_src = _fetch_kp()
        if effective_level >= 2 and lat_used is not None:
            wx_code, wx_src = _fetch_weather(lat_used, lon_model)
        else:
            wx_code, wx_src = 0, 'skipped'  # bez pogody przy level 0/1
    else:
        kp, kp_src = 2.0, 'offline'
        wx_code, wx_src = 0, 'offline'

    df_d = _df_daily(utc_hour, lon_model)
    df_k = _df_kp(kp)

    freq = max(6.0, min(10.0, F_BASE + df_d + df_k))
    period_ms = 1000 / freq
    virtue_ms = period_ms / 6

    wx_mod, wx_label = _weather_code_to_mod(wx_code)

    # sigma_mod: Kp + pogoda lokalna (mnożniki niezależne)
    sigma_mod = (1.0 + 0.06 * kp) * wx_mod

    # source: live jeśli choć jedno źródło online
    source = 'live' if (kp_src == 'live' or wx_src == 'live') else 'offline'

    seed_component = int(freq * 1000) + int(utc_hour) * 10000 + int(wx_mod * 100)

    return dict(
        freq=round(freq, 4),
        kp=kp,
        source=source,
        kp_source=kp_src,
        df_daily=round(df_d, 4),
        df_kp=round(df_k, 4),
        weather_code=wx_code,
        weather_label=wx_label,
        weather_source=wx_src,
        weather_mod=round(wx_mod, 4),
        period_ms=round(period_ms, 2),
        virtue_ms=round(virtue_ms, 2),
        sigma_mod=round(sigma_mod, 4),
        seed_component=seed_component,
        utc=now.strftime('%H:%M UTC'),
        local_hour=round((utc_hour + lon_model / 15) % 24, 2),
        location_level=effective_level,
    )


def print_status(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON):
    s = get_schumann(lat=lat, lon=lon)
    tag = f"[{s['source'].upper()}]"
    print(f"Schumann @ ({lat}N, {lon}E) — {s['utc']} (local {s['local_hour']:.1f}h) {tag}")
    print(f"  f          = {s['freq']:.4f} Hz  "
          f"(base {F_BASE} + daily {s['df_daily']:+.4f} + Kp {s['df_kp']:+.4f})")
    print(f"  Kp         = {s['kp']} [{s['kp_source']}]")
    print(f"  pogoda     = {s['weather_label']} (code={s['weather_code']}) "
          f"[{s['weather_source']}]  wx_mod={s['weather_mod']}")
    print(f"  period     = {s['period_ms']:.1f}ms  |  virtue = {s['virtue_ms']:.1f}ms/cnota")
    print(f"  sigma_mod  = {s['sigma_mod']:.4f}  (Kp×wx)")
    if s['source'] == 'offline':
        print(f"  ⚠ offline — Kp=2.0, pogoda=clear, tylko model dzienny")
    print(f"  Mars f ≈ {F_MARS} Hz  ({F_MARS/s['freq']:.3f}× lokalnego)")


if __name__ == '__main__':
    print_status()
