"""Schritt 2: Kleiner OCT-Interferometer-Testchip.

Bausteine (definiert in pic_lib.py):
  oct_mzi          MZI mit 1x2-Splitter und 2x2-Ausgangskoppler
                   (zwei gegenphasige Ausgaenge -> balancierte Detektion wie im OCT)
  oct_mzi_with_gc  dasselbe mit Gitterkopplern (127-µm-Raster, Loopback) und Beschriftung

Hier: vier Varianten mit unterschiedlichem Delta L untereinander als Testchip.

Ausfuehren:  F5 in Spyder (KLayout mit klive offen lassen)
Ergebnis:    gds/step2_oct_testchip.gds
"""
from pathlib import Path

import gdsfactory as gf

import pic_lib

gf.clear_cache()   # Zwischenspeicher leeren, damit Code-Aenderungen beim erneuten Lauf wirken

DELTAS = (10, 50, 100, 200)   # Gangunterschiede in µm


@gf.cell
def oct_testchip(deltas: tuple[float, ...] = DELTAS) -> gf.Component:
    """Testchip: Varianten untereinander. gf.grid: shape = (Zeilen, Spalten)."""
    devices = [pic_lib.oct_mzi_with_gc(delta_length=d) for d in deltas]
    return gf.grid(devices, spacing=(50, 50), shape=(len(deltas), 1))


for d in DELTAS:
    print(f"dL = {d:>4} µm  ->  FSR ≈ {pic_lib.fsr_nm(d):5.1f} nm")

chip = oct_testchip()
print("Chipgroesse:", round(chip.xsize), "x", round(chip.ysize), "µm")

out = Path("gds")
out.mkdir(exist_ok=True)
chip.write_gds(out / "step2_oct_testchip.gds")
chip.show()
