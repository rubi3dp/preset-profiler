# Preset Profiler – Anleitung

Plugin für OrcaSlicer · rubi3dp.de · Stand 10.11.26 (Version 0.9.0)

## Was das Plugin macht

Der Preset Profiler zeigt alle **eigenen** Drucker-, Filament- und Prozessprofile übersichtlich in einem Fenster in Orca – mit Zuordnung, Prüfungen und Unterschieden zum Elternprofil. Dazu kommen:

- **Prüfungen** – findet typische Fehler in Bindungen und Kalibrierprofilen (Liste unten).
- **Änderungen** – zeigt, welche Werte sich seit dem letzten bestätigten Stand geändert haben, z. B. nach einem Update der Systemprofile.
- **Datenblätter** – ein Blatt je Filament mit Grund- und Maßkalibrierung, für Tablet oder Ausdruck.
- **Export** – CSV-Dateien und eine HTML-Übersicht.

Das Plugin **liest nur**. Es ändert keine Profile, geht nicht ins Internet und schreibt nur in die Ordner, die du selbst festlegst.

**Worum es geht – und worum nicht:** Der Preset Profiler ist kein Profil-Editor. Bearbeitet wird weiter in Orca. Er ist dafür da, die Profildaten schnell herauszubekommen und den Überblick zu behalten – direkt in Orca, ohne Zusatzprogramm. Werkzeuge wie „Slicer Preset Studio“ (Helio Additive) sind eigenständige Programme zum Bearbeiten, Duplizieren und Sammeländern von Presets; der Preset Profiler setzt dagegen auf Übersicht, Prüfungen, Änderungen nach Updates und Datenblätter.

## Voraussetzungen

- OrcaSlicer 2.5 oder neuer (Python-Plugins).
- Getestet auf macOS. Windows und Linux sind vorgesehen, aber noch nicht getestet – Rückmeldungen sind willkommen.

## Installation

1. In Orca: **Plugins › Install local plugin** und die Datei `preset_profiler.py` wählen.
2. OrcaSlicer neu starten.

**Neue Version installieren:** altes Plugin deinstallieren, neue Datei installieren, Orca neu starten. Ein Überschreiben/Aktualisieren bietet Orca bei lokalen Plugins nicht an.

**Umstieg von „Profilübersicht“:** Das Plugin hieß früher „Profilübersicht“. Altes Plugin deinstallieren, `preset_profiler.py` installieren. Einstellungen, Vergleichsstand und Datenblatt-Liste werden automatisch übernommen. Die Ordner-Abfrage beim Neustart bitte erneut bestätigen.

## Einrichten

Plugins › **Preset Profiler – Einstellungen** ausführen oder in der Übersicht auf **⚙ Einstellungen** klicken:

| Feld | Bedeutung |
|---|---|
| Zielordner | Hierhin gehen CSV- und HTML-Export. Leer = nur in den Plugin-Ordner von Orca. |
| kal-Zusatz | Wort im Profilnamen, das kalibrierte Profile kennzeichnet, z. B. `kal`. Leer = aus. |
| Sprache | Deutsch oder Englisch (im Fenster jederzeit umschaltbar, die Wahl wird gemerkt). |
| Datenblatt-Ordner | Hierhin werden Datenblätter geschrieben. |
| Beim Start öffnen | Übersicht öffnet sich nach dem Start von Orca (nur einlesen, nichts schreiben). |
| Beim Start exportieren | Export beim Start in den Zielordner. |
| Beim Start auf geänderte Profile hinweisen | Bei Änderungen startet die Übersicht auf dem Reiter „Änderungen“ – oder es kommt eine Meldung, wenn die Übersicht nicht automatisch öffnet. |
| Weitere Slicer einlesen | Liest zusätzlich die eigenen Profile weiterer Slicer (derzeit Bambu Studio), nur lesen. Danach Orca neu starten und den Lesezugriff bestätigen. |
| Datenblatt-Felder | Zwei freie Felder (Beschriftung + Vorgabe), z. B. „Ersteller“ / „Projekt“. |

**Wichtig zu den Ordnern:** Orca bietet Plugins keine Ordnerauswahl – den Pfad bitte einfügen. Mac: Ordner im Finder markieren, ⌥⌘C. Windows: Ordner markieren, Strg+Umschalt+C. Ordner werden vom Plugin nicht angelegt.

Nach dem Ändern eines Ordners **Orca neu starten** und die Abfrage zum Ordnerzugriff bestätigen. Orca vergibt Ordnerfreigaben nur beim Start.

**Weitere Slicer:** In der ersten Spalte zeigt ein Kästchen die Quelle: O = OrcaSlicer, B = Bambu Studio. Markierungen (kal, Drucker, K) erscheinen in der Farbe des jeweiligen Slicers. Mit den Knöpfen OrcaSlicer / Bambu Studio / Alle lässt sich die Ansicht umschalten; beim Start sind die Orca-Profile aktiv. Datenblätter heißen „O – …“ bzw. „B – …“; Blätter mit altem Namen meldet das Plugin einmal zum Löschen. Zuordnung und Prüfungen beziehen sich nur auf Studio-Drucker. Den Pressure Advance ermittelt Bambu Studio automatisch – bei Studio-Profilen steht deshalb „auto“. Studio kennt Schrumpf nur für XY.

## Das Fenster

Plugins › **Preset Profiler** ausführen (oder automatisch beim Start). Das Fenster dockt unten an.

- **Reiter:** Zuordnung (welches Profil an welchem Drucker) · Filament · Prozess · Drucker · Änderungen.
- **Filter:** Drucker, Typ, Hersteller, Grundprofile/kal-Profile, „nur Auffällige“, Suche.
- **Zeile anklicken** öffnet alle Werte des Profils mit den Abweichungen zum Elternprofil; erneuter Klick schließt.
- **„gilt für“-Kärtchen:**
  - gefüllt = kal-Profil · Rahmen = direkt an eigenen Drucker gebunden
  - gestrichelt = nur über den Systemnamen gebunden
  - gepunktet = Systemdrucker ohne eigenes Druckerprofil
  - rot durchgestrichen = gebundener Drucker existiert nicht mehr
  - nur Modellname (z. B. „P1S“) = gilt für alle Düsen dieses Modells (Bedingung `printer_model == "…"`)
- **Braune Werte mit ²** = mehrere Werte je Hotend-Variante (z. B. Standard / High Flow; in Bambu Studio bis zu sechs). Angezeigt wird der erste, Maus drauf zeigt alle mit Variantennamen.
- **↻ Neu einlesen** liest die Profile neu ein. Nach dem Speichern eines Profils aktualisiert sich die Übersicht von selbst.

## Prüfungen

| Kürzel | Bedeutung |
|---|---|
| B0 | Bindung leer – Profil gilt für alle Drucker |
| V | kein eigener Drucker |
| BT | gebunden an einen Drucker, den es nicht mehr gibt |
| BD | Kompatibilitätsbedingung gesetzt, die das Plugin nicht auswerten kann |
| NB | Name passt nicht zur Bindung (Drucker/Düse im Namen ≠ gebundener Drucker) |
| PL | leerer Eintrag in der Zuordnung – Profil wird in Orca überall ausgeblendet |
| KP | zugeordneter Prozess existiert nicht (umbenannt/gelöscht) |
| K2 | kal-Profil an mehr als einem Drucker |
| KW | Korrekturwerte gesetzt (Schrumpf ≠ 100 % bzw. Loch-/Konturkorrektur ≠ 0) |
| K? | kal-Profil ohne Korrekturwerte |
| KN | Korrekturwerte ohne kal-Zusatz im Namen |
| HU | Hotend unklar – mehrere Varianten, aber kein `Hotend:` in der Notiz |
| HW | `Hotend:` in der Notiz passt zu keiner Variante im Profil |

## Änderungen

Der Reiter vergleicht die aktuellen Werte mit einem gespeicherten Stand. Neue, entfernte und geänderte Werte werden aufgelistet – auch solche, die ein Update der Systemprofile still verändert hat.

**Übernehmen** macht die aktuellen Werte zur neuen Vergleichsbasis; die Liste wird geleert. Beim ersten Lauf wird der Stand still angelegt.

## Datenblätter

- **Datenblatt erstellen** (im Detailfenster eines Filaments) oder **Alle Datenblätter erstellen** (oben).
- Vor dem Erstellen lassen sich die zwei Felder anpassen (Vorgabe aus den Einstellungen).
- Gibt es das Blatt schon, fragt das Plugin nach: überschreiben / nur neue / abbrechen.
- Danach listet es Blätter auf, die zu keinem Profil mehr passen. Löschen musst du sie selbst.

**Inhalt:**
- Oben **Grundkalibrierung:** Temperaturen, Lüfter, MVF, PA, Flow, Rückzug (nur, wenn das Filament eigene Werte setzt).
- Darunter, bei kal-Profilen, **Maßkalibrierung:** Schrumpf XY/Z, Flow und aus dem zugeordneten Prozess Schichthöhe, Linienbreiten, Loch-/Konturkorrektur, Elefantenfuß, Wandreihenfolge, präzise Außenwand.
- Ein **Notizfeld** füllt den Rest der Seite.

**Format:** eine Seite im A4-Seitenverhältnis – auf dem Tablet hochkant vollständig lesbar, druckbar in A4/A5. Als PDF: Blatt im Browser öffnen, ggf. Notiz eintippen, „Als PDF exportieren“ bzw. drucken (der getippte Text wird mitgedruckt).

**Sprache:** Das Blatt übernimmt die Sprache, die im Fenster beim Erstellen eingestellt ist.

## Empfohlene Profilnamen (damit die Prüfungen greifen)

- **Elternprofil Filament:** ohne Düse, gilt für alle Düsen eines Modells, z. B. `Jayo PETG P1S`.
- **Kind je Düse:** gemessen und geprüft, Düse im Namen, z. B. `Jayo PETG P1S 0.4`.
- **kal-Profil:** abgekoppelt, Drucker vor Düse, kal-Zusatz am Ende, z. B. `Jayo PETG grün Plus5 0.4 kal`. Im Notizfeld: `Basis: … · Stand TT.MM.JJ` und bei mehreren Hotend-Varianten zusätzlich die gemessene Variante, z. B. `Hotend: Standard`, `Hotend: High Flow`, `Hotend: E3D High Flow` oder `Hotend: Bowden Standard` („Direct Drive“ kann entfallen).
- **kal-Prozess:** `LH0.20 <Filament> <Drucker> <Düse> kal`, dem kal-Filament zugeordnet.

## Exportdateien

`drucker.csv`, `filament.csv`, `prozess.csv` (alle Werte je Profil), `unterschiede.csv` (Abweichungen zum Elternprofil), `uebersicht.html` (die Übersicht zum Öffnen im Browser).

## Grenzen

- Keine Ordnerauswahl per Klick (bietet Orca für Plugins nicht an).
- Nur eigene Profile; Systemprofile erscheinen nur als Elternprofil zum Vergleich.
- Ungespeicherte Änderungen sieht das Plugin nur, solange das Profil in Orca offen ist.
- Die Änderungsliste unterscheidet nicht, ob du einen Wert selbst geändert hast oder ein Update.
