#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Website Blocker
File: main.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
CLI entry & launcher for the Website Blocker project. Defaults to opening the GUI if no args provided.

Usage:
python -m website_blocker
python -m website_blocker --block example.com badsite.com
python -m website_blocker --unblock example.com
python -m website_blocker --list
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .hosts_manager import HostsManager
from .gui import run_gui
from .exceptions import HostsPermissionError, HostsFileError, InvalidDomainError
from ._version import __version__

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="website-blocker", description="Block/unblock websites via hosts file.")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--block", nargs="+", help="Domains/URLs to block.")
    grp.add_argument("--unblock", nargs="+", help="Domains/URLs to unblock.")
    p.add_argument("--list", action="store_true", help="List blocked domains and exit.")
    p.add_argument("--hosts-path", type=Path, help="Custom hosts file path (for testing).")
    p.add_argument("--no-backup", action="store_true", help="Write without creating .bak backup.")
    p.add_argument("--version", action="store_true", help="Print version and exit.")
    return p.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.version:
        print(__version__)
        return 0

    manager = HostsManager(hosts_path=args.hosts_path, backup=(not args.no_backup))

    # No args → open GUI
    if not (args.block or args.unblock or args.list):
        run_gui()
        return 0

    try:
        if args.block:
            added = manager.block(args.block)
            print(f"Added {added} rule(s).")
        if args.unblock:
            removed = manager.unblock(args.unblock)
            print(f"Removed {removed} rule(s).")
        if args.list:
            for d in manager.list_blocked():
                print(d)
        return 0
    except InvalidDomainError as exc:
        print(f"Invalid domain: {exc}", file=sys.stderr)
        return 2
    except HostsPermissionError as exc:
        print(f"Permission error: {exc}\nTry running as administrator/root.", file=sys.stderr)
        return 3
    except HostsFileError as exc:
        print(f"Hosts file error: {exc}", file=sys.stderr)
        return 4

if __name__ == "__main__":
    raise SystemExit(main())
