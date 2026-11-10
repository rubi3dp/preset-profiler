# Preset Profiler – Guide

Plugin for OrcaSlicer · rubi3dp.de · as of 10.11.26 (version 0.9.0)

## What the plugin does

Preset Profiler shows all of your **own** printer, filament and process profiles in one window inside Orca – with assignments, checks and differences to the parent profile. On top of that:

- **Checks** – finds typical mistakes in bindings and calibrated profiles (list below).
- **Changes** – shows which values changed since the last accepted state, e.g. after an update of the system profiles.
- **Data sheets** – one sheet per filament with base and dimensional calibration, for tablet or print.
- **Export** – CSV files and an HTML overview.

The plugin **only reads**. It never changes profiles, never goes online and only writes to folders you choose yourself.

**What it is – and what it isn't:** Preset Profiler is not a preset editor; you keep editing in Orca. It is there to get your preset data out quickly and keep track of it – right inside Orca, no extra program. Tools like “Slicer Preset Studio” (Helio Additive) are standalone programs for editing, duplicating and batch-changing presets; Preset Profiler focuses on overview, checks, changes after updates and data sheets.

## Requirements

- OrcaSlicer 2.5 or newer (Python plugins).
- Tested on macOS. Windows and Linux are supported in principle but not yet tested – feedback welcome.

## Installation

1. In Orca: **Plugins › Install local plugin** and select `preset_profiler.py`.
2. Restart OrcaSlicer.

**Installing a new version:** uninstall the old plugin, install the new file, restart Orca. Orca does not offer overwrite/update for local plugins.

**Coming from “Profilübersicht”:** the plugin used to be called “Profilübersicht”. Uninstall it and install `preset_profiler.py`. Settings, the comparison baseline and the data sheet list are taken over automatically. Confirm the folder access prompt again after restarting.

## Setup

Run Plugins › **Preset Profiler – Settings** (shown as “Einstellungen” while the plugin language is German):

| Field | Meaning |
|---|---|
| Target folder | CSV and HTML export goes here. Empty = Orca's plugin folder only. |
| Calibration tag | Word in the profile name that marks calibrated profiles, e.g. `kal`. Empty = off. |
| Language | German or English (can be switched in the window at any time). |
| Data sheet folder | Data sheets are written here. |
| Open when Orca starts | The overview opens after Orca starts (reads only, writes nothing). |
| Export when Orca starts | Export to the target folder at start. |
| Notify about changed profiles at start | If there are changes, the overview opens on the “Changes” tab – or a message appears if the overview does not open automatically. |
| Data sheet fields | Two free fields (label + default), e.g. “Author” / “Project”. |

**About folders:** Orca does not offer plugins a folder picker – please paste the path. Mac: select the folder in Finder, ⌥⌘C. Windows: select the folder, Ctrl+Shift+C. The plugin never creates folders.

After changing a folder, **restart Orca** and confirm the folder access prompt. Orca only grants folder access at start.

## The window

Run Plugins › **Preset Profiler** (or automatically at start). The window docks at the bottom.

- **Tabs:** Matrix (which profile on which printer) · Filament · Process · Printer · Changes.
- **Filters:** printer, type, vendor, base/calibrated, “issues only”, search.
- **Click a row** to see all values of the profile with the differences to its parent; click again to close.
- **“Applies to” chips:**
  - filled = calibrated profile · outlined = bound directly to an own printer
  - dashed = bound via system name only
  - dotted = system printer without own printer profile
  - red, struck through = bound printer no longer exists
  - model name only (e.g. “P1S”) = valid for all nozzles of that model (condition `printer_model == "…"`)
- **Brown values with ²** = two values (standard hotend / high-flow hotend). The first is shown; hover to see both.
- **↻ Reload** reads the profiles again. After saving a profile the overview updates by itself.

## Checks

| Code | Meaning |
|---|---|
| B0 | Empty binding – profile applies to all printers |
| V | No own printer |
| BT | Bound to a printer that no longer exists |
| BD | Compatibility condition set that the plugin cannot evaluate |
| NB | Name does not match binding (printer/nozzle in the name ≠ bound printer) |
| PL | Empty entry in the assignment – Orca hides the profile everywhere |
| KP | Assigned process does not exist (renamed/deleted) |
| K2 | Calibrated profile bound to more than one printer |
| KW | Correction values set (shrink ≠ 100 % or hole/contour compensation ≠ 0) |
| K? | Calibrated profile without correction values |
| KN | Correction values without calibration tag in the name |
| HU | Hotend unclear – two variants, but no `Hotend:` in the notes |
| HW | `Hotend:` in the notes does not match the profile's variant |

## Changes

The tab compares current values with a saved state. New, removed and changed values are listed – including values silently changed by an update of the system profiles.

**Accept** makes the current values the new baseline; the list is cleared. On first run the baseline is created silently.

## Data sheets

- **Create data sheet** (in a filament's detail panel) or **Create all data sheets** (top).
- Before creating, the two fields can be adjusted (defaults from the settings).
- If a sheet already exists, the plugin asks: overwrite / new only / cancel.
- Afterwards it lists sheets that no longer match any profile. You delete those yourself.

**Content:**
- Top: **base calibration** – temperatures, fan, max volumetric speed, PA, flow, retraction (only if the filament sets its own values).
- Below, for calibrated profiles: **dimensional calibration** – shrink XY/Z, flow and, from the assigned process, layer height, line widths, hole/contour compensation, elephant foot, wall order, precise outer wall.
- A **notes field** fills the rest of the page.

**Format:** one page in A4 aspect ratio – fully readable on a tablet in portrait, printable on A4/A5. For a PDF: open the sheet in a browser, type a note if you like, then “Export as PDF” or print (typed text is printed too).

**Language:** the sheet uses the language set in the window when it is created.

## Recommended profile names (so the checks work)

- **Filament parent:** no nozzle, valid for all nozzles of a model, e.g. `Jayo PETG P1S`.
- **Child per nozzle:** measured and verified, nozzle in the name, e.g. `Jayo PETG P1S 0.4`.
- **Calibrated profile:** detached, printer before nozzle, calibration tag at the end, e.g. `Jayo PETG green Plus5 0.4 kal`. In the notes: `Basis: … · Stand DD.MM.YY` and, with two hotend variants, also `Hotend: Standard` or `Hotend: High Flow`.
- **Calibrated process:** `LH0.20 <filament> <printer> <nozzle> kal`, assigned to the calibrated filament.

## Export files

`drucker.csv` (printers), `filament.csv`, `prozess.csv` (processes) – all values per profile; `unterschiede.csv` (differences to the parent); `uebersicht.html` (the overview to open in a browser).

## Limitations

- No folder picker (Orca does not offer one to plugins).
- Own profiles only; system profiles only appear as parents for comparison.
- Unsaved changes are only visible while the profile is open in Orca.
- The change list cannot tell whether you changed a value or an update did.
