# Sound List Manager — Project Walkthrough

A single running record of the steps taken to build the Sound List Manager: a CLI and (later) a GUI for viewing and editing a list of sounds (`name`, `description`, `file_path`) backed by a shared `sounds.csv` file.

## Step 1: Plan the CLI

Initial planning defined the data model and program flow before any code was written:

- **Data model**: each sound is a record with `name`, `description`, `file_path`. CSV header: `name,description,file_path`.
- **File I/O layer**: `load_sounds(csv_path)` reads the CSV into a list of dicts at startup (creating the file with a header if missing, tolerating a missing/empty file); `save_sounds(csv_path, sounds)` rewrites the full list after every change.
- **Core operations**: list all sounds, add a new one, edit an existing one (selected by name or index), delete one (with a y/n confirmation).
- **Menu system**: a loop that prints a keyword menu (`list`, `add`, `edit`, `delete`, `exit`) and dispatches on user input, re-prompting on unrecognized keywords.
- **Exit handling**: the `exit` keyword saves any pending changes and breaks the loop safely.
- **Error handling**: guard against blank/duplicate names, invalid selectors, and wrap file I/O in try/except.

## Step 2: Implement the CLI

The plan was implemented in [sound_manager.py](sound_manager.py):

- `ensure_csv`, `load_sounds`, `save_sounds` — CSV I/O, including resetting the file if the header is unexpected and skipping malformed rows with a warning.
- `display_sounds` — prints a formatted table of all sounds.
- `find_sound_by_name` / `find_sound_index` — lookup by case-insensitive name or 1-based index, used by edit/delete.
- `prompt_for_sound`, `add_sound`, `edit_sound`, `delete_sound` — interactive add/edit/delete, each guarding against blank names, duplicate names, and saving to CSV immediately after a change.
- `print_menu` and `main` — the keyword-driven menu loop (`list`/`ls`/`show`, `add`, `edit`, `delete`, `exit`/`quit`), saving before exit.

Sample data was seeded in [sounds.csv](sounds.csv) (ambient/background sounds like Ambient Rain, Desk Fan, Beach Waves, etc.) for testing.

## Step 3: Plan a GUI — first attempt with PyQt6

To give the CLI a graphical front end without changing its behavior, a GUI plan was drafted around **PyQt6**:

- Reuse the existing data layer (`load_sounds`, `save_sounds`, `find_sound_by_name`, `find_sound_index`) from `sound_manager.py` rather than duplicating CSV logic.
- `QMainWindow` with a `QTableWidget` for the sound list, Add/Edit/Delete/Refresh buttons, a File → Exit menu, and a status bar for feedback.
- A reusable `QDialog` for both Add and Edit, with `QFileDialog` for browsing to a sound file.
- `QMessageBox` for delete confirmation and error reporting.
- `closeEvent` override to save before the window closes.

## Step 4: Pivot to Tkinter

After building and testing an initial PyQt6 version, the project moved to **Tkinter** for the GUI instead — Tkinter ships with the standard library, so it avoids the extra PyQt6 dependency while covering the same requirements for this project's scope. The GUI plan and implementation were redone using Tkinter's equivalents of the original PyQt6 design:

| PyQt6 concept | Tkinter equivalent |
|---|---|
| `QMainWindow` | `tk.Tk` main window |
| `QTableWidget` | `ttk.Treeview` (columns: name, description, file_path) |
| `QDialog` (Add/Edit) | `tk.Toplevel` modal-style dialog |
| `QFileDialog` | `tkinter.filedialog.askopenfilename` |
| `QMessageBox` | `tkinter.messagebox` (warning/error/askyesno) |
| `closeEvent` | `protocol("WM_DELETE_WINDOW", ...)` |
| Status bar label | `ttk.Label` bound to a `StringVar` |

## Step 5: Implement the Tkinter GUI

Implemented in [sound_manager_gui.py](sound_manager_gui.py), importing `load_sounds`, `save_sounds`, and `find_sound_by_name` directly from `sound_manager.py` so both interfaces stay data-compatible:

- **`SoundDialog`** (`tk.Toplevel`) — shared Add/Edit form with Name, Description, and File Path fields, a Browse button (filtered to common audio extensions), OK/Cancel, Enter-to-accept/Escape-to-cancel bindings, and a blank-name guard.
- **`SoundManagerApp`** (`tk.Tk`) — main window with:
  - A toolbar: Add, Edit, Delete, Refresh buttons.
  - A `ttk.Treeview` table (Name / Description / File Path columns), double-click to edit, selection-driven enabling/disabling of Edit and Delete.
  - A status bar showing the result of the last action (loaded count, added/updated/deleted sound, or a failure message).
  - A File → Exit menu item wired to the same exit path as the window's close button.
  - `add_sound` / `edit_selected_sound` / `delete_selected_sound`, each mirroring the CLI's rules: blank-name rejection, duplicate-name rejection (case-insensitive), immediate `save_sounds` after every change, and a `messagebox` error if the save fails.
  - `on_exit` — saves before closing; if the save fails, asks the user whether to exit anyway.

## Step 6: Add a Play button

A **Play** button was added to `gui.py`'s toolbar, next to Add/Edit/Delete/Refresh:

- Enabled/disabled together with Edit and Delete based on Treeview selection (`update_button_states`).
- `play_selected_sound` reads the selected row's `file_path`, resolves it relative to the CSV's directory if it isn't absolute, and opens it with the OS default handler: `os.startfile` on Windows, `open` (via `subprocess.Popen`) on macOS, `xdg-open` on Linux.
- Guards against a blank `file_path` (warning) and a missing file on disk (error), mirroring the `messagebox` error style used elsewhere in the GUI.
- Sets the status bar to `Playing: <name>` on success.
- No timeline, volume slider, or other transport controls were added — playback is a single fire-and-forget action handed off to the OS's default player, matching the scope of this step.

## Current Project State

```
sound_manager.py        CLI + shared data layer (load/save/find functions)
sound_manager_gui.py    Tkinter GUI, built on top of sound_manager.py
sounds.csv              Shared data file used by both interfaces
```

Both interfaces read and write the same `sounds.csv`, using the same validation rules (no blank names, no duplicate names, case-insensitive matching), so switching between the CLI and the GUI mid-session is safe.

## Possible Next Steps

- Search/filter box above the Treeview to hide non-matching rows.
- Click-to-sort on Treeview column headers.
- Playback controls beyond the basic Play button: a timeline/seek bar, a volume slider, pause/stop.
- Drag-and-drop a file onto the File Path field.
- Automated tests for the shared data layer (`load_sounds`/`save_sounds`/`find_sound_by_name`) so both UIs stay verified against the same behavior.
