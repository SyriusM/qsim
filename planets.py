"""
Planetary resonance driver dla qsim.
Każda planeta ma pozycję ekliptyczną (0-360°).
Heksagon dzieli zodiak na 6 sektorów po 60° = 6 cnót.
Planeta w sektorze cnoty → wzmocnienie tej cnoty w sigma_mod.

Mapowanie sektorów:
  Odwaga      0-60°   (Baran-Byk)
  Pokora     60-120°   (Byk-Bliźnięta)
  Przebaczenie 120-180° (Bliźnięta-Rak)
  Współczucie 180-240° (Rak-Lew)
  Wdzięczność 240-300° (Lew-Panna)
  Rozumienie  300-360° (Panna-Waga→Ryby)

Rezonans planety z cnotą = cos²(Δkąt / 2), Δkąt = odległość od środka sektora.
Offline-safe: fallback = uniform [1]*6.
"""

import math
import datetime

try:
    import ephem
    _EPHEM_OK = True
except ImportError:
    _EPHEM_OK = False

from hexagon import HEXAGON

DEFAULT_LAT = '50.3'
DEFAULT_LON = '18.7'

# Wagi planet (klasyczne: szybkie planety słabsze, wolne silniejsze dla tła)
PLANET_WEIGHTS = {
    'Sun':     1.5,
    'Moon':    1.2,
    'Mercury': 0.8,
    'Venus':   1.0,
    'Mars':    1.2,
    'Jupiter': 1.4,
    'Saturn':  1.3,
    'Uranus':  0.9,
    'Neptune': 0.9,
}

# Środki sektorów cnót na ekliptyce (°)
VIRTUE_CENTERS = {v: i * 60 + 30 for i, v in enumerate(HEXAGON)}
# odwaga=30°, pokora=90°, przebaczenie=150°, współczucie=210°, wdzięczność=270°, rozumienie=330°


def _angular_dist(a: float, b: float) -> float:
    """Kątowa odległość między dwoma pozycjami ekliptycznymi [0-360°]. Zwraca [0-180°]."""
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _resonance(planet_lon: float, virtue_center: float) -> float:
    """
    Rezonans 2D (tylko ekliptyka) = cos²(Δ/2). Astrologia.
    """
    d = _angular_dist(planet_lon, virtue_center)
    return math.cos(math.radians(d / 2)) ** 2


def _virtue_3d_vector(virtue_center_deg: float) -> tuple[float, float, float]:
    """
    Wektor 3D cnoty na sferze jednostkowej w płaszczyźnie ekliptyki.
    Cnota leży w płaszczyźnie XY (lat=0), azymut = virtue_center.
    """
    phi = math.radians(virtue_center_deg)
    return (math.cos(phi), math.sin(phi), 0.0)


def _resonance_3d(x: float, y: float, z: float, virtue_center_deg: float,
                   r_scale: float = 1.0) -> float:
    """
    Rezonans 3D: cos²(kąt między wektorem planety a wektorem cnoty).
    Uwzględnia odchylenie od ekliptyki (lat_ekl) i normalizuje przez |r|.
    r_scale: skalowanie wagowe odległości (1.0=geometria, <1=bliskie silniejsze).
    """
    vx, vy, vz = _virtue_3d_vector(virtue_center_deg)
    r_planet = math.sqrt(x*x + y*y + z*z)
    if r_planet == 0:
        return 0.0
    # Jednostkowy wektor planety
    ux, uy, uz = x/r_planet, y/r_planet, z/r_planet
    cos_angle = ux*vx + uy*vy + uz*vz
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle = math.acos(cos_angle)
    return math.cos(angle / 2) ** 2


def get_planetary_strengths(lat: str = DEFAULT_LAT,
                             lon: str = DEFAULT_LON,
                             dt: datetime.datetime | None = None,
                             mode: str = '3d') -> dict:
    """
    Oblicz virtue strengths [0-1] z aktualnych pozycji planet.
    mode='2d' — tylko ekliptyka (astrologia klasyczna)
    mode='3d' — pełne 3D heliocentric (z deklinacją i odległością)
    Zwraca dict z 'strengths' (lista 6), 'planets' (pozycje), 'source'.
    Offline-safe: jeśli brak ephem → uniform.
    """
    if not _EPHEM_OK:
        return dict(
            strengths=[1.0] * 6,
            planets={},
            source='offline_no_ephem',
            note='ephem not installed — pip install ephem',
        )

    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)

    obs = ephem.Observer()
    obs.lat = lat
    obs.lon = lon
    obs.date = dt

    planet_objects = {
        'Sun':     ephem.Sun(),
        'Moon':    ephem.Moon(),
        'Mercury': ephem.Mercury(),
        'Venus':   ephem.Venus(),
        'Mars':    ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn':  ephem.Saturn(),
        'Uranus':  ephem.Uranus(),
        'Neptune': ephem.Neptune(),
    }

    # Pobierz pozycje ekliptyczne (2D) + 3D heliocentric
    planet_data = {}
    for name, planet in planet_objects.items():
        planet.compute(obs)
        ecl = ephem.Ecliptic(planet)
        lon_deg = math.degrees(ecl.lon) % 360
        lat_deg = math.degrees(ecl.lat)
        # 3D heliocentric (x,y,z in AU)
        if name == 'Sun':
            x3d, y3d, z3d = 0.0, 0.0, 0.0
            r_hel = 0.0
        elif name == 'Moon':
            # Księżyc: geocentric, pomijamy w 3D helio
            x3d = y3d = z3d = 0.0
            r_hel = planet.earth_distance
        else:
            r_hel = planet.sun_distance
            hlon = planet.hlon
            hlat = planet.hlat
            x3d = r_hel * math.cos(hlat) * math.cos(hlon)
            y3d = r_hel * math.cos(hlat) * math.sin(hlon)
            z3d = r_hel * math.sin(hlat)
        planet_data[name] = dict(
            lon=lon_deg, lat=lat_deg,
            x=x3d, y=y3d, z=z3d, r=r_hel,
        )

    # Oblicz siłę każdej cnoty
    raw_strengths = []
    for virtue in HEXAGON:
        vc = VIRTUE_CENTERS[virtue]
        if mode == '3d':
            total = 0.0
            for p, d in planet_data.items():
                if d['r'] == 0 and p != 'Sun':
                    # Księżyc / brak 3D — fallback 2D
                    total += PLANET_WEIGHTS[p] * _resonance(d['lon'], vc)
                elif p == 'Sun':
                    # Słońce w centrum — nie ma kąta, bierzemy lon ekliptyki
                    total += PLANET_WEIGHTS[p] * _resonance(d['lon'], vc)
                else:
                    total += PLANET_WEIGHTS[p] * _resonance_3d(d['x'], d['y'], d['z'], vc)
        else:
            total = sum(
                PLANET_WEIGHTS[p] * _resonance(d['lon'], vc)
                for p, d in planet_data.items()
            )
        raw_strengths.append(total)

    # Normalizuj: max → 1.0
    mx = max(raw_strengths) if max(raw_strengths) > 0 else 1.0
    strengths = [s / mx for s in raw_strengths]

    signs = ['Baran','Byk','Bliź','Rak','Lew','Panna',
             'Waga','Skor','Strz','Koz','Wod','Ryby']
    planet_info = {
        p: dict(lon=round(d['lon'], 2),
                lat=round(d['lat'], 3),
                sign=signs[int(d['lon'] / 30)],
                deg=round(d['lon'] % 30, 1),
                r_au=round(d['r'], 4))
        for p, d in planet_data.items()
    }

    return dict(
        strengths=strengths,
        planets=planet_info,
        source='live',
        mode=mode,
        dt_utc=dt.strftime('%Y-%m-%d %H:%M UTC'),
        virtue_centers=VIRTUE_CENTERS,
    )


def print_planetary_status(lat: str = DEFAULT_LAT, lon: str = DEFAULT_LON):
    r = get_planetary_strengths(lat=lat, lon=lon)
    print(f"Planetary resonance @ {lat}N {lon}E — {r.get('dt_utc','?')} [{r['source']}]")
    print()
    print('  Planety:')
    for name, info in r.get('planets', {}).items():
        w = PLANET_WEIGHTS.get(name, 1.0)
        lon_s = f'{info["lon"]:>7.2f}'
        print(f'    {name:<10} {lon_s}°  {info["sign"]} {info["deg"]:.1f}°  (w={w})')
    print()
    print('  Virtue strengths z planet:')
    for v, s in zip(HEXAGON, r['strengths']):
        bar = '█' * int(s * 15) + '░' * (15 - int(s * 15))
        vc = VIRTUE_CENTERS[v]
        print(f'    {v:<15} {bar} {s:.4f}  (centrum sektora={vc}°)')


if __name__ == '__main__':
    print_planetary_status()
