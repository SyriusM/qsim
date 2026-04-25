"""
qsim sovereignty — programmatic audit of the project's network surface.

Run: `python -m qsim.sovereignty audit`  (lub: `python sovereignty.py audit`)

This module is the runtime counterpart of LICENSE §3. It declares — in code —
exactly what endpoints upstream qsim contacts. Forks that add network calls
MUST extend NETWORK_SURFACE here (and update LICENSE §3) per LICENSE §2.3.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkEndpoint:
    module: str
    endpoint: str
    direction: str  # "local→local", "local→public", "local→private"
    user_data: str
    optin_flag: str
    notes: str = ""


# Upstream qsim network surface — keep in sync with LICENSE §3
NETWORK_SURFACE: tuple[NetworkEndpoint, ...] = (
    NetworkEndpoint(
        module="schumann._fetch_kp",
        endpoint="https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
        direction="local→public",
        user_data="none (public Kp index, GET only)",
        optin_flag="get_schumann(live=True)  [default]",
        notes="Fallback Kp=2.0 if offline. No API key.",
    ),
    NetworkEndpoint(
        module="schumann._fetch_weather",
        endpoint="https://api.open-meteo.com/v1/forecast",
        direction="local→public",
        user_data="lat/lon as GET params (only at location_level>=2)",
        optin_flag="get_schumann(live=True, location_level=2)",
        notes="Skipped at location_level 0/1. Fallback code=0 if offline. No API key.",
    ),
)

EXTERNAL_ENDPOINTS = tuple(
    e for e in NETWORK_SURFACE if e.direction == "local→public"
)


def audit() -> int:
    print("qsim — Sovereignty Audit")
    print("=" * 70)
    print(f"Total endpoints: {len(NETWORK_SURFACE)}")
    print(f"External (local→public): {len(EXTERNAL_ENDPOINTS)}")
    print()
    for i, ep in enumerate(NETWORK_SURFACE, 1):
        print(f"[{i}] {ep.module}")
        print(f"    endpoint:   {ep.endpoint}")
        print(f"    direction:  {ep.direction}")
        print(f"    user data:  {ep.user_data}")
        print(f"    opt-in:     {ep.optin_flag}")
        if ep.notes:
            print(f"    notes:      {ep.notes}")
        print()
    if EXTERNAL_ENDPOINTS:
        print(f"⚠ {len(EXTERNAL_ENDPOINTS)} external endpoint(s).")
        print("  All are public, key-less, with offline fallbacks.")
        print("  Disable: pass live=False to schumann.get_schumann().")
    else:
        print("✓ No external endpoints.")
    print()
    print("See LICENSE §2 (Sovereignty Conditions) and §3 (full audit).")
    return 0


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "audit":
        return audit()
    print("Usage: python -m qsim.sovereignty audit", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
