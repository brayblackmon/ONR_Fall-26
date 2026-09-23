#!/usr/bin/env python3
"""Tkinter GUI for the sound list manager."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

from sound_manager import find_sound_by_name, load_sounds, save_sounds


class SoundDialog(tk.Toplevel):
    """Dialog for adding or editing a sound record."""

    def __init__(self, parent, sound: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        self.title("Add Sound" if sound is None else "Edit Sound")
        self.geometry("480x220")
        self.resizable(False, False)

        self.sound = sound.copy() if sound else {"name": "", "description": "", "file_path": ""}

        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.name_var = tk.StringVar(value=self.sound.get("name", ""))
        self.name_entry = ttk.Entry(self, textvariable=self.name_var, width=50)
        self.name_entry.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.description_var = tk.StringVar(value=self.sound.get("description", ""))
        self.description_entry = ttk.Entry(self, textvariable=self.description_var, width=50)
        self.description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(self, text="File Path:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.file_var = tk.StringVar(value=self.sound.get("file_path", ""))
        self.file_entry = ttk.Entry(self, textvariable=self.file_var, width=38)
        self.file_entry.grid(row=2, column=1, padx=(10, 5), pady=5, sticky="ew")

        browse_button = ttk.Button(self, text="Browse...", command=self.choose_file)
        browse_button.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="ew")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=(10, 15), sticky="e")

        ok_button = ttk.Button(button_frame, text="OK", command=self._accept)
        ok_button.pack(side="left", padx=(0, 5))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left")

        self.grid_columnconfigure(1, weight=1)
        self.bind("<Return>", lambda event: self._accept())
        self.bind("<Escape>", lambda event: self.destroy())

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a sound file",
            initialdir=os.getcwd(),
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac *.m4a *.aac"), ("All Files", "*.*")],
        )
        if file_path:
            self.file_var.set(file_path)

    def _accept(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Invalid Input", "Sound name cannot be blank.")
            return
        self.result = self.get_data()
        self.destroy()

    def get_data(self) -> Dict[str, str]:
        return {
            "name": self.name_var.get().strip(),
            "description": self.description_var.get().strip(),
            "file_path": self.file_var.get().strip(),
        }


class SoundManagerApp(tk.Tk):
    """Main tkinter window for managing sound records."""

    def __init__(self):
        super().__init__()
        self.title("Sound List Manager")
        self.geometry("900x500")
        self.minsize(700, 350)

        self.csv_path = os.path.join(os.path.dirname(__file__), "sounds.csv")
        self.sounds: List[Dict[str, str]] = []

        self.create_menu()
        self.create_widgets()
        self.load_sounds()

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        self.add_button = ttk.Button(toolbar, text="Add", command=self.add_sound)
        self.add_button.pack(side="left", padx=(0, 5))

        self.edit_button = ttk.Button(toolbar, text="Edit", command=self.edit_selected_sound)
        self.edit_button.pack(side="left", padx=(0, 5))

        self.delete_button = ttk.Button(toolbar, text="Delete", command=self.delete_selected_sound)
        self.delete_button.pack(side="left", padx=(0, 5))

        self.refresh_button = ttk.Button(toolbar, text="Refresh", command=self.refresh_table)
        self.refresh_button.pack(side="left")

        self.table = ttk.Treeview(self, columns=("name", "description", "file_path"), show="headings")
        self.table.heading("name", text="Name")
        self.table.heading("description", text="Description")
        self.table.heading("file_path", text="File Path")
        self.table.column("name", width=180, anchor="w")
        self.table.column("description", width=260, anchor="w")
        self.table.column("file_path", width=320, anchor="w")
        self.table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.table.bind("<Double-1>", lambda event: self.edit_selected_sound())
        self.table.bind("<<TreeviewSelect>>", lambda event: self.update_button_states())

        self.status_var = tk.StringVar(value="Loading sounds...")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(fill="x", padx=10, pady=(0, 10))

        self.update_button_states()

    def update_button_states(self):
        selection = self.table.selection()
        has_selection = bool(selection)
        self.edit_button.state(["!disabled"] if has_selection else ["disabled"])
        self.delete_button.state(["!disabled"] if has_selection else ["disabled"])

    def load_sounds(self):
        try:
            self.sounds = load_sounds(self.csv_path)
            self.refresh_table()
            self.status_var.set(f"Loaded {len(self.sounds)} sound(s)")
        except OSError as exc:
            messagebox.showerror("Error", f"Unable to access the sound database: {exc}")
            self.status_var.set("Load failed")

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for sound in self.sounds:
            self.table.insert(
                "",
                "end",
                values=(sound.get("name", ""), sound.get("description", ""), sound.get("file_path", "")),
            )

        self.update_button_states()

    def add_sound(self):
        dialog = SoundDialog(self)
        self.wait_window(dialog)
        if not hasattr(dialog, "result"):
            return

        data = dialog.result
        if not data["name"].strip():
            messagebox.showwarning("Invalid Input", "Sound name cannot be blank.")
            return

        if find_sound_by_name(self.sounds, data["name"]):
            messagebox.showwarning("Duplicate Name", f"A sound named '{data['name']}' already exists.")
            return

        self.sounds.append(data)
        try:
            save_sounds(self.csv_path, self.sounds)
            self.refresh_table()
            self.status_var.set(f"Added sound: {data['name']}")
        except OSError as exc:
            messagebox.showerror("Save Failed", f"Could not save sound list: {exc}")

    def edit_selected_sound(self):
        selection = self.table.selection()
        if not selection:
            return

        row_id = selection[0]
        row_index = self.table.index(row_id)
        current = self.sounds[row_index]

        dialog = SoundDialog(self, sound=current)
        self.wait_window(dialog)
        if not hasattr(dialog, "result"):
            return

        updated = dialog.result
        if not updated["name"].strip():
            messagebox.showwarning("Invalid Input", "Sound name cannot be blank.")
            return

        if updated["name"].lower() != current["name"].lower() and find_sound_by_name(self.sounds, updated["name"]):
            messagebox.showwarning("Duplicate Name", f"A sound named '{updated['name']}' already exists.")
            return

        self.sounds[row_index] = updated
        try:
            save_sounds(self.csv_path, self.sounds)
            self.refresh_table()
            self.status_var.set(f"Updated sound: {updated['name']}")
        except OSError as exc:
            messagebox.showerror("Save Failed", f"Could not save sound list: {exc}")

    def delete_selected_sound(self):
        selection = self.table.selection()
        if not selection:
            return

        row_index = self.table.index(selection[0])
        target = self.sounds[row_index]
        if not messagebox.askyesno("Confirm Delete", f"Delete '{target['name']}'?"):
            return

        del self.sounds[row_index]
        try:
            save_sounds(self.csv_path, self.sounds)
            self.refresh_table()
            self.status_var.set(f"Deleted sound: {target['name']}")
        except OSError as exc:
            messagebox.showerror("Save Failed", f"Could not save sound list: {exc}")

    def on_exit(self):
        try:
            save_sounds(self.csv_path, self.sounds)
            self.destroy()
        except OSError as exc:
            if messagebox.askyesno("Save Failed", f"Could not save before exit: {exc}\n\nExit anyway?"):
                self.destroy()
