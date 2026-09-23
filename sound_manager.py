#!/usr/bin/env python3
"""Core CSV data layer and application entry point for the sound manager."""

import csv
import os
from typing import Dict, List, Optional

CSV_HEADER = ["name", "description", "file_path"]


def ensure_csv(csv_path: str) -> None:
    """Create the CSV file with a header if it does not exist yet."""
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)


def load_sounds(csv_path: str) -> List[Dict[str, str]]:
    """Load sound records from the CSV, skipping malformed rows."""
    ensure_csv(csv_path)

    sounds: List[Dict[str, str]] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
        return sounds

    header = [cell.strip().lower() for cell in rows[0]]
    if header != CSV_HEADER:
        print(f"Warning: CSV header is unexpected: {rows[0]}. Resetting header.")
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)
        return sounds

    for index, row in enumerate(rows[1:], start=2):
        if len(row) != 3:
            print(f"Skipping malformed row {index}: {row}")
            continue

        name, description, file_path = [cell.strip() for cell in row]
        if not any([name, description, file_path]):
            continue

        sounds.append({
            "name": name,
            "description": description,
            "file_path": file_path,
        })

    return sounds


def save_sounds(csv_path: str, sounds: List[Dict[str, str]]) -> None:
    """Persist all sounds back to the CSV."""
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(sounds)


def find_sound_by_name(sounds: List[Dict[str, str]], name: str) -> Optional[Dict[str, str]]:
    """Find a sound by case-insensitive name."""
    target = name.strip().lower()
    for sound in sounds:
        if sound.get("name", "").strip().lower() == target:
            return sound
    return None


def find_sound_index(sounds: List[Dict[str, str]], selector: str) -> Optional[int]:
    """Return the index for a name or 1-based numeric selector."""
    selector = selector.strip()
    if not selector:
        return None

    if selector.isdigit():
        index = int(selector)
        if 1 <= index <= len(sounds):
            return index - 1
        return None

    for index, sound in enumerate(sounds):
        if sound.get("name", "").strip().lower() == selector.lower():
            return index

    return None


def main() -> None:
    """Launch the Tkinter application from the main module."""
    from gui import SoundManagerApp

    app = SoundManagerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_exit)
    app.mainloop()


if __name__ == "__main__":
    main()
