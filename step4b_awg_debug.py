"""Schritt 4b: AWG-Parameter systematisch pruefen (Routing + DRC).

Problem aus Schritt 4: Mit length_increment = 20 µm schlaegt das interne Routing des
AWG fehl ("too small to safely place bends"), weil der Abstand der beiden
Star Coupler (fpr_spacing) zu klein ist.

Dieses Skript baut das AWG fuer mehrere Kombinationen, prueft, ob gdsfactory beim
Routing warnt, und laesst fuer jede Variante den DRC laufen.

Ergebnis:
  - Routing: Arm i bekommt einen Umweg der Hoehe i * dL / 2. Zwei Boegen mit 10 µm
    Radius brauchen >= 20 µm -> erst ab dL >= 40 µm routen alle Arme fehlerfrei.
  - DRC: fpr_spacing = 50 µm laesst die Arme ueberlappen (Abstandsfehler);
    ab 100 µm ist der DRC sauber.
  -> Uebernommen in pic_lib.awg_spectrometer: dL = 40 µm, fpr_spacing = 100 µm.

Voraussetzung: pic_lib.py liegt im selben Ordner.
"""
import warnings
from pathlib import Path

import gdsfactory as gf

import pic_lib

gf.clear_cache()

OUT = Path("gds") / "awg_debug"
OUT.mkdir(parents=True, exist_ok=True)

FPR_SPACINGS = (50, 100, 150)    # Abstand der Star Coupler in µm
LENGTH_INCREMENTS = (5, 10, 20, 40, 50, 60)   # Laengenunterschied benachbarter Arme in µm

print(" dL   fpr_sp   Routing   Breite  Abstand   Groesse")
results = []
for dl in LENGTH_INCREMENTS:
    for fpr in FPR_SPACINGS:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            awg = gf.components.awg(
                arms=10, outputs=3, length_increment=dl, fpr_spacing=fpr
            )
        routing_ok = not any("Routing failed" in str(w.message) for w in caught)

        gds = OUT / f"awg_dl{dl}_fpr{fpr}.gds"
        awg.write_gds(gds)
        n_errors = pic_lib.run_drc(gds)
        results.append((dl, fpr, routing_ok, n_errors, gds))
        print(
            f"{dl:3}   {fpr:6}   {'OK' if routing_ok else 'FEHLER':7}   "
            f"DRC gesamt: {n_errors:4}   {awg.xsize:.0f} x {awg.ysize:.0f} µm"
        )

ok = [r for r in results if r[2]]
if ok:
    best = min(ok, key=lambda r: (r[3], r[1]))
    print(f"\nBeste Variante mit sauberem Routing: dL={best[0]} µm, fpr_spacing={best[1]} µm,"
          f" DRC-Fehler: {best[3]}  -> {best[4]}")
    gf.components.awg(
        arms=10, outputs=3, length_increment=best[0], fpr_spacing=best[1]
    ).show()
else:
    print("\nKeine Variante ohne Routingfehler gefunden.")
