"""Schritt 3: Eigener Design Rule Check (DRC) mit der KLayout-Python-Bibliothek.

Ablauf:
  1. Eine Testzelle mit ABSICHTLICHEN Regelverstoessen erzeugen
  2. DRC auf die Testzelle und auf den Testchip aus Schritt 2 anwenden
  3. Fehler als Report (.lyrdb) speichern -> in KLayout im Marker Browser ansehen

Regeln (vereinfachte Beispielwerte, nicht von einer echten Foundry):
  WG.W.1  Mindestbreite Wellenleiter-Ebene   0.15 µm
  WG.S.1  Mindestabstand Wellenleiter-Ebene  0.15 µm

Ausfuehren:  F5 in Spyder (Schritt 2 muss vorher gelaufen sein)
"""
from pathlib import Path

import gdsfactory as gf
import klayout.db as kdb
import klayout.rdb as krdb

try:
    gf.gpdk.PDK.activate()
except AttributeError:
    pass

gf.clear_cache()

WG_LAYER = (1, 0)
MIN_WIDTH_UM = 0.15
MIN_SPACE_UM = 0.15
OUT = Path("gds")
OUT.mkdir(exist_ok=True)


# --- 1. Testzelle mit absichtlichen Fehlern ----------------------------------------
@gf.cell
def drc_test_cell() -> gf.Component:
    """Zwei Wellenleiter mit 0.1 µm Spalt und ein 0.1 µm schmaler Streifen."""
    c = gf.Component()
    wg1 = c << gf.components.straight(length=20, width=0.5)
    wg2 = c << gf.components.straight(length=20, width=0.5)
    wg2.movey(0.6)     # Mitten 0.6 µm auseinander, Breite 0.5 -> Spalt 0.1 µm (Fehler WG.S.1)

    thin = c << gf.components.rectangle(size=(20, 0.1), layer=WG_LAYER)
    thin.movey(5)      # nur 0.1 µm breit (Fehler WG.W.1)
    return c


# --- 2. DRC-Funktion ----------------------------------------------------------------
def run_drc(gds_path: Path) -> int:
    """Prueft Mindestbreite und -abstand auf der WG-Ebene. Gibt die Fehlerzahl zurueck."""
    layout = kdb.Layout()
    layout.read(str(gds_path))
    top = layout.top_cell()
    dbu = layout.dbu  # Datenbankeinheit in µm (meist 0.001 = 1 nm)

    layer_index = layout.find_layer(*WG_LAYER)
    if layer_index is None:
        print(f"{gds_path.name}: Ebene {WG_LAYER} nicht gefunden")
        return 0

    # Alle Polygone der WG-Ebene aus der gesamten Hierarchie einsammeln und verschmelzen.
    # merge() ist wichtig: Aneinanderstossende Teilstuecke wuerden sonst als
    # "zu nah beieinander" gemeldet, obwohl sie physikalisch eine Flaeche sind.
    region = kdb.Region(top.begin_shapes_rec(layer_index))
    region.merge()

    width_errors = region.width_check(round(MIN_WIDTH_UM / dbu))
    space_errors = region.space_check(round(MIN_SPACE_UM / dbu))

    # Report fuer den KLayout Marker Browser
    rdb = krdb.ReportDatabase("DRC")
    rdb_cell = rdb.create_cell(top.name)
    cat_w = rdb.create_category(f"WG.W.1 min width {MIN_WIDTH_UM} um")
    cat_s = rdb.create_category(f"WG.S.1 min space {MIN_SPACE_UM} um")
    trans = kdb.CplxTrans(dbu)
    rdb.create_items(rdb_cell.rdb_id(), cat_w.rdb_id(), trans, width_errors)
    rdb.create_items(rdb_cell.rdb_id(), cat_s.rdb_id(), trans, space_errors)
    report = gds_path.with_suffix(".lyrdb")
    rdb.save(str(report))

    n_w, n_s = width_errors.count(), space_errors.count()
    status = "OK" if n_w + n_s == 0 else "FEHLER"
    print(f"{gds_path.name}: {status}  Breite: {n_w}  Abstand: {n_s}  -> {report}")
    return n_w + n_s


# --- 3. Ausfuehren ---------------------------------------------------------------------
test = drc_test_cell()
test_gds = OUT / "step3_drc_test.gds"
test.write_gds(test_gds)

run_drc(test_gds)                               # erwartet: 2 Fehler
run_drc(OUT / "step2_oct_testchip.gds")         # erwartet: sauber

test.show()
