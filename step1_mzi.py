"""Schritt 1: Erstes Mach-Zehnder-Interferometer (MZI) mit gdsfactory.

Ausführen:  python step1_mzi.py
Ergebnis:   step1_mzi.gds (öffnet sich automatisch in KLayout, wenn klive läuft)
"""
import gdsfactory as gf

# Generisches Lern-PDK aktivieren (gdsfactory 10); in Version 9 ist es schon aktiv.
try:
    gf.gpdk.PDK.activate()
except AttributeError:
    pass

# Gangunterschied der beiden Arme in µm – das Pendant zur Referenzarm-Länge im OCT
DELTA_L = 50.0

c = gf.components.mzi(delta_length=DELTA_L)

# Ports anzeigen: Name, Position und Ausrichtung jedes optischen Anschlusses
c.pprint_ports()

# Freier Spektralbereich (FSR) grob abschätzen: FSR = lambda^2 / (n_g * delta_L)
wavelength_um = 1.55   # C-Band
n_g = 4.2              # typischer Gruppenindex eines Si-Streifenwellenleiters
fsr_nm = wavelength_um**2 / (n_g * DELTA_L) * 1e3
print(f"delta_L = {DELTA_L} µm  ->  FSR ≈ {fsr_nm:.1f} nm")

c.write_gds("step1_mzi.gds")
c.show()  # schickt das Layout an KLayout (klive-Plugin muss laufen)
