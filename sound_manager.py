#!/usr/bin/env python3
"""Simple sound list manager based on the Week3 CLI plan."""

# Import modules
import csv
import os
import sys
from typing import List, Dict, Optional

# Instantiate variable(s)
CSV_HEADER = ["name", "description", "file_path"]

# CSV file error handling (file path)
def ensure_csv(csv_path: str) -> None:
    """Create the CSV file with a header if it does not exist yet."""
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)



# CSV reading function w/ built-in error handling for malformed data
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



# CSV write function
def save_sounds(csv_path: str, sounds: List[Dict[str, str]]) -> None:
    """Persist all sounds back to the CSV."""
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(sounds)



# List function using data read from CSV
def display_sounds(sounds: List[Dict[str, str]]) -> None:
    """Print a readable, simple table of all sounds."""
    if not sounds:
        print("No sounds available.")
        return

    print("\nCurrent sounds:")
    print("-" * 78)
    print(f"{'#':<3} {'Name':<20} {'Description':<30} {'File path'}")
    print("-" * 78)

    for index, sound in enumerate(sounds, start=1):
        name = sound.get("name", "")
        description = sound.get("description", "")
        file_path = sound.get("file_path", "")
        print(f"{index:<3} {name:<20} {description:<30} {file_path}")

    print("-" * 78)



# Indexing function for deletion & edits
def find_sound_by_name(sounds: List[Dict[str, str]], name: str) -> Optional[Dict[str, str]]:
    """Find a sound by case-insensitive name."""
    target = name.strip().lower()
    for sound in sounds:
        if sound.get("name", "").strip().lower() == target:
            return sound
    return None


# Indexing function for finding name or numeric selector
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



# User input prompt function
def prompt_for_sound() -> Dict[str, str]:
    """Ask the user for name, description, and file path."""
    name = input("Sound name: ").strip()
    while not name:
        print("Name cannot be blank.")
        name = input("Sound name: ").strip()

    description = input("Description: ").strip()
    file_path = input("File path: ").strip()
    if not file_path:
        file_path = ""  # keep it valid but informative

    return {
        "name": name,
        "description": description,
        "file_path": file_path,
    }



# Append function
def add_sound(sounds: List[Dict[str, str]], csv_path: str) -> None:
    """Add a new sound to the list and save it."""
    new_sound = prompt_for_sound()
    if find_sound_by_name(sounds, new_sound["name"]):
        print(f"A sound named '{new_sound['name']}' already exists.")
        return

    sounds.append(new_sound)
    save_sounds(csv_path, sounds)
    print(f"Added sound: {new_sound['name']}")



# Editing attributes 
def edit_sound(sounds: List[Dict[str, str]], csv_path: str) -> None:
    """Edit a sound selected by index or name."""
    if not sounds:
        print("There are no sounds to edit.")
        return

    selector = input("Select a sound by name or index: ").strip()
    index = find_sound_index(sounds, selector)
    if index is None:
        print("No matching sound found.")
        return

    current = sounds[index]
    print(f"Editing: {current['name']}")

    new_name = input(f"New name [{current['name']}]: ").strip()
    new_description = input(f"New description [{current['description']}]: ").strip()
    new_path = input(f"New file path [{current['file_path']}]: ").strip()

    if new_name:
        if new_name.lower() != current['name'].lower() and find_sound_by_name(sounds, new_name):
            print(f"A sound named '{new_name}' already exists.")
            return
        current["name"] = new_name
    if new_description:
        current["description"] = new_description
    if new_path:
        current["file_path"] = new_path

    save_sounds(csv_path, sounds)
    print(f"Updated sound: {current['name']}")



# Deletion with extra prompt for safety
def delete_sound(sounds: List[Dict[str, str]], csv_path: str) -> None:
    """Delete a sound after confirmation."""
    if not sounds:
        print("There are no sounds to delete.")
        return

    selector = input("Delete which sound by name or index? ").strip()
    index = find_sound_index(sounds, selector)
    if index is None:
        print("No matching sound found.")
        return

    target = sounds[index]
    confirm = input(f"Delete '{target['name']}'? (y/n): ").strip().lower()
    if confirm not in {"y", "yes"}:
        print("Delete cancelled.")
        return

    removed = sounds.pop(index)
    save_sounds(csv_path, sounds)
    print(f"Deleted sound: {removed['name']}")


# Legacy CLI menu kept commented out while the GUI version is being developed.
# def print_menu() -> None:
#     """Display the command menu."""
#     print("\nAvailable commands:")
#     print("[list]   Show all sounds")
#     print("[add]    Add a new sound")
#     print("[edit]   Edit a sound")
#     print("[delete] Delete a sound")
#     print("[exit]   Quit the program")
#
#
# def main() -> None:
#     csv_path = os.path.join(os.path.dirname(__file__), "sounds.csv")
#
#     try:
#         sounds = load_sounds(csv_path)
#     except OSError as exc:
#         print(f"Unable to access the sound database: {exc}")
#         sys.exit(1)
#
#     print("Sound List CLI")
#     while True:
#         print_menu()
#         command = input("Enter command: ").strip().lower()
#
#         if command in {"list", "ls", "show"}:
#             display_sounds(sounds)
#         elif command == "add":
#             add_sound(sounds, csv_path)
#         elif command == "edit":
#             edit_sound(sounds, csv_path)
#         elif command == "delete":
#             delete_sound(sounds, csv_path)
#         elif command in {"exit", "quit"}:
#             try:
#                 save_sounds(csv_path, sounds)
#             except OSError as exc:
#                 print(f"Warning: could not save before exiting: {exc}")
#             print("Goodbye.")
#             break
#         else:
#             print("Unknown command. Please choose from list, add, edit, delete, or exit.")
#
#
# if __name__ == "__main__":
#     main()
