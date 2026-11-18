"""Schritt 2b: Interferometer mit Spiral-Verzoegerungsleitung ("Schnecke") im Referenzarm.

Idee (OCT on a chip):
  Der Probenarm verlaesst im echten System den Chip und laeuft durch Luft und Auge.
  Damit Referenz- und Probenarm optisch gleich lang sind, braucht der Referenzarm auf
  dem Chip eine lange Wellenleiterstrecke. Die wird platzsparend zur Spirale aufgewickelt.
  Laenge und Querschnitt der Spirale bestimmen auch, wie viel Dispersion der
  Referenzarm einbringt (Dispersionsanpassung zwischen den Armen).

Bausteine (definiert in pic_lib.py):
  spiral_delay            Spirale mit gegebener Laenge
  oct_delay_mzi           1x2-Splitter, oberer Arm direkt, unterer Arm ueber Spirale, 2x2-Combiner
  oct_delay_mzi_with_gc   dasselbe mit Gitterkopplern und Beschriftung

Ausfuehren:  F5 in Spyder (KLayout mit klive offen lassen)
Ergebnis:    gds/step2b_oct_spiral_delay.gds
"""
from pathlib import Path

import gdsfactory as gf

import pic_lib
from pic_lib import N_G, WAVELENGTH_UM

gf.clear_cache()

C_UM_PER_PS = 299.792458   # Lichtgeschwindigkeit in µm/ps
LENGTHS = (1000, 2000, 5000)   # Spirallaengen in µm


@gf.cell
def oct_delay_chip(lengths: tuple[float, ...] = LENGTHS) -> gf.Component:
    devices = [pic_lib.oct_delay_mzi_with_gc(length_ref=L) for L in lengths]
    return gf.grid(devices, spacing=(50, 100), shape=(len(lengths), 1))


print(" L_ref    opt. Weg n_g*L   Laufzeit   FSR      Spiralflaeche")
for L in LENGTHS:
    sp = pic_lib.spiral_delay(L)
    print(
        f"{L / 1000:4.1f} mm   {N_G * L / 1000:6.1f} mm      {N_G * L / C_UM_PER_PS:6.1f} ps  "
        f"{WAVELENGTH_UM**2 / (N_G * L) * 1e6:6.1f} pm   {sp.xsize:.0f} x {sp.ysize:.0f} µm"
    )

chip = oct_delay_chip()
print("Chipgroesse:", round(chip.xsize), "x", round(chip.ysize), "µm")

out = Path("gds")
out.mkdir(exist_ok=True)
chip.write_gds(out / "step2b_oct_spiral_delay.gds")
chip.show()
