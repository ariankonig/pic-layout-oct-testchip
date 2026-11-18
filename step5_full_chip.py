"""Schritt 5: Gesamtchip mit allen Strukturen, Rahmen und Titel, plus DRC.

Inhalt (von oben nach unten):
  1. OCT-on-chip-System: Spiral-Interferometer -> AWG, alle Ports mit Gitterkopplern
  2. AWG-Teststruktur (Spektrometer allein)
  3. Spiral-Interferometer mit 1 mm und 2 mm Referenzlaenge
  4. MZI-Referenzen mit Delta L = 50 µm und 200 µm
Jede Teststruktur hat eine Loopback-Schleife (Justage, Verlustreferenz).

Der Chiprahmen liegt auf der Floorplan-Ebene 64/0. Der DRC laeuft ueber den ganzen
Chip; die freigegebenen Gitterkoppler-Zellen sind als Waiver ausgenommen.

Ausfuehren:  F5 in Spyder (KLayout mit klive offen lassen)
Ergebnis:    gds/step5_full_chip.gds
"""
from pathlib import Path

import gdsfactory as gf

import pic_lib
from pic_lib import TEXT_LAYER

gf.clear_cache()

FLOORPLAN_LAYER = (64, 0)
BLOCK_SPACING = 80      # vertikaler Abstand zwischen den Bloecken in µm
MARGIN = 50             # Abstand zum Chiprahmen in µm
AWG_DL = 40.0


@gf.cell
def full_chip() -> gf.Component:
    c = gf.Component()

    blocks = [
        pic_lib.oct_on_chip_with_gc(length_ref=1000, awg_dl=AWG_DL),
        pic_lib.awg_test_structure(length_increment=AWG_DL),
        pic_lib.oct_delay_mzi_with_gc(length_ref=1000),
        pic_lib.oct_delay_mzi_with_gc(length_ref=2000),
        pic_lib.oct_mzi_with_gc(delta_length=50),
        pic_lib.oct_mzi_with_gc(delta_length=200),
    ]

    # Bloecke untereinander stapeln, linksbuendig
    y = 0.0
    for block in blocks:
        ref = c << block
        ref.xmin = 0
        ref.ymax = y
        y = ref.ymin - BLOCK_SPACING

    title = c << gf.components.text(
        text="OCT on chip test chip - A Koenig 2026", size=20, layer=TEXT_LAYER
    )
    title.xmin = 0
    title.ymin = 30

    # Chiprahmen um alles herum
    xmin, xmax, ymin, ymax = c.xmin, c.xmax, c.ymin, c.ymax
    frame = c << gf.components.rectangle(
        size=(xmax - xmin + 2 * MARGIN, ymax - ymin + 2 * MARGIN), layer=FLOORPLAN_LAYER
    )
    frame.xmin = xmin - MARGIN
    frame.ymin = ymin - MARGIN
    return c


chip = full_chip()
print(f"Chipgroesse: {chip.xsize / 1000:.2f} x {chip.ysize / 1000:.2f} mm")

out = Path("gds")
out.mkdir(exist_ok=True)
gds = out / "step5_full_chip.gds"
chip.write_gds(gds)
pic_lib.run_drc(gds)
chip.show()
