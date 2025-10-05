#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Website Blocker
File: gui.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Tkinter GUI for blocking/unblocking domains using HostsManager. Designed to be minimal and robust.

Usage:
python -m website_blocker  # opens GUI by default
"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List

from .hosts_manager import HostsManager
from .exceptions import HostsPermissionError, HostsFileError, InvalidDomainError

class WebsiteBlockerApp(tk.Tk):
    def __init__(self, manager: HostsManager | None = None) -> None:
        super().__init__()
        self.title("Website Blocker")
        self.geometry("520x420")
        self.resizable(False, False)

        self.manager = manager or HostsManager()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        # Entry
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack(fill="x")
        tk.Label(frm, text="Domain or URL (e.g., example.com):").pack(anchor="w")
        self.entry = tk.Entry(frm)
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", lambda _e: self.on_block())

        # Buttons
        btns = tk.Frame(self, padx=10, pady=6)
        btns.pack(fill="x")
        tk.Button(btns, text="Block", command=self.on_block, width=12).pack(side="left")
        tk.Button(btns, text="Unblock", command=self.on_unblock_selected, width=12).pack(side="left", padx=6)
        tk.Button(btns, text="Unblock…", command=self.on_unblock_prompt, width=12).pack(side="left")
        tk.Button(btns, text="Refresh", command=self._refresh_list, width=10).pack(side="right")

        # Listbox
        lstfrm = tk.Frame(self, padx=10, pady=8)
        lstfrm.pack(fill="both", expand=True)
        tk.Label(lstfrm, text="Currently blocked domains:").pack(anchor="w")
        self.listbox = tk.Listbox(lstfrm, height=14)
        self.listbox.pack(fill="both", expand=True)

        # Status
        self.status = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status, anchor="w", bd=1, relief="sunken").pack(fill="x", side="bottom")

    def _refresh_list(self) -> None:
        try:
            blocked = self.manager.list_blocked()
        except (HostsPermissionError, HostsFileError) as exc:
            messagebox.showerror("Error", str(exc))
            blocked = []
        self.listbox.delete(0, tk.END)
        for d in blocked:
            self.listbox.insert(tk.END, d)
        self.status.set(f"Loaded {len(blocked)} blocked domains.")

    def on_block(self) -> None:
        dom = self.entry.get().strip()
        if not dom:
            messagebox.showinfo("Input required", "Please enter a domain or URL.")
            return
        try:
            added = self.manager.block([dom])
            if added:
                self.status.set(f"Blocked: {dom}")
                self._refresh_list()
            else:
                self.status.set(f"Already blocked: {dom}")
        except InvalidDomainError as exc:
            messagebox.showwarning("Invalid Domain", str(exc))
        except HostsPermissionError as exc:
            messagebox.showerror("Permission Required", f"{exc}\n\nTry running as administrator/root.")
        except HostsFileError as exc:
            messagebox.showerror("Hosts Error", str(exc))

    def on_unblock_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Select domain", "Select a domain from the list to unblock.")
            return
        domain = self.listbox.get(sel[0])
        try:
            removed = self.manager.unblock([domain])
            if removed:
                self.status.set(f"Unblocked: {domain}")
                self._refresh_list()
            else:
                self.status.set(f"Was not blocked: {domain}")
        except (HostsPermissionError, HostsFileError) as exc:
            messagebox.showerror("Error", str(exc))

    def on_unblock_prompt(self) -> None:
        dom = simpledialog.askstring("Unblock domain", "Domain or URL to unblock:")
        if not dom:
            return
        try:
            removed = self.manager.unblock([dom])
            self.status.set(f"Unblocked: {dom}" if removed else f"Not found: {dom}")
            self._refresh_list()
        except (HostsPermissionError, HostsFileError) as exc:
            messagebox.showerror("Error", str(exc))

def run_gui() -> None:
    app = WebsiteBlockerApp()
    app.mainloop()
