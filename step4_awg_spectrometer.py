"""Schritt 4: On-Chip-Spektrometer (AWG) und OCT-on-a-chip-Demonstrator, mit DRC.

Teil A: AWG allein, mit Gitterkopplern als Teststruktur
Teil B: Interferometer mit Spirale (aus Schritt 2b) -> AWG
        = Grundprinzip eines Spectral-Domain-OCT auf dem Chip
Danach laeuft der DRC aus pic_lib auf beide Layouts.

Die AWG-Parameter (dL = 40 µm, fpr_spacing = 100 µm) stammen aus Schritt 4b.

Ausfuehren:  F5 in Spyder (KLayout mit klive offen lassen)
"""
from pathlib import Path

import gdsfactory as gf

import pic_lib

gf.clear_cache()

AWG_DL = 40.0        # Laengenunterschied benachbarter AWG-Arme in µm (>= 40, siehe Schritt 4b)
L_REF = 1000.0       # Spirallaenge im Referenzarm in µm
OUT = Path("gds")
OUT.mkdir(exist_ok=True)

print(f"AWG: dL = {AWG_DL:g} µm  ->  FSR ≈ {pic_lib.fsr_nm(AWG_DL):.1f} nm")

a = pic_lib.awg_test_structure(length_increment=AWG_DL)
b = pic_lib.oct_on_chip(length_ref=L_REF, awg_dl=AWG_DL)
print("AWG-Teststruktur:", round(a.xsize), "x", round(a.ysize), "µm")
print("OCT-on-chip:     ", round(b.xsize), "x", round(b.ysize), "µm")

gds_a = OUT / "step4_awg_test.gds"
gds_b = OUT / "step4_oct_on_chip.gds"
a.write_gds(gds_a)
b.write_gds(gds_b)

pic_lib.run_drc(gds_a)
pic_lib.run_drc(gds_b)

b.show()
