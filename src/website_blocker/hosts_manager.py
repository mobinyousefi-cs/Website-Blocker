#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Website Blocker
File: hosts_manager.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Core logic for blocking/unblocking domains by editing the system hosts file (cross-platform).
Safe-by-default parsing; idempotent operations; easy to unit-test by injecting a custom hosts path.

Usage:
from website_blocker.hosts_manager import HostsManager
hm = HostsManager()  # uses system hosts path
hm.block(["example.com", "www.bad.com"])
hm.unblock(["example.com"])
print(hm.is_blocked("www.bad.com"))

Notes:
- Requires elevated privileges to modify the real system hosts file.
- Windows: C:\\Windows\\System32\\drivers\\etc\\hosts
- Linux/macOS: /etc/hosts
"""

from __future__ import annotations
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set

from .exceptions import HostsPermissionError, HostsFileError, InvalidDomainError

DEFAULT_REDIRECT_IP = "127.0.0.1"
RULE_MARKER = "# website-blocker"

_DOMAIN_RE = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*"
    r"(?:\.[A-Za-z]{2,63})$"
)

def _normalize_domain(value: str) -> str:
    value = value.strip().lower()
    # Strip scheme and path if user pasted a URL
    value = re.sub(r"^https?://", "", value)
    value = value.split("/")[0]
    value = value.split(":")[0]  # strip port
    if not value or value in {"localhost"}:
        raise InvalidDomainError(f"Invalid or unsupported domain: {value!r}")
    if not _DOMAIN_RE.match(value):
        raise InvalidDomainError(f"Invalid domain: {value!r}")
    return value

def _detect_hosts_path() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "drivers" / "etc" / "hosts"
    return Path("/etc/hosts")

@dataclass(frozen=True)
class BlockRule:
    domain: str
    redirect_ip: str = DEFAULT_REDIRECT_IP

    def line(self) -> str:
        return f"{self.redirect_ip} {self.domain} {RULE_MARKER}"

class HostsManager:
    """
    Manages blocking rules in the hosts file. Public methods are idempotent.
    """
    def __init__(self, hosts_path: Path | None = None, backup: bool = True) -> None:
        self.hosts_path = hosts_path or _detect_hosts_path()
        self.backup = backup

    # ---------- Internal helpers ----------
    def _read(self) -> List[str]:
        try:
            return self.hosts_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except PermissionError as exc:
            raise HostsPermissionError(
                f"Insufficient permissions to read hosts file at {self.hosts_path}"
            ) from exc
        except OSError as exc:
            raise HostsFileError(f"Failed to read hosts file: {exc}") from exc

    def _write(self, lines: List[str]) -> None:
        try:
            if self.backup:
                shutil.copy2(self.hosts_path, f"{self.hosts_path}.bak")
            text = "\n".join(lines) + "\n"
            self.hosts_path.write_text(text, encoding="utf-8")
        except PermissionError as exc:
            raise HostsPermissionError(
                f"Insufficient permissions to write hosts file at {self.hosts_path}"
            ) from exc
        except OSError as exc:
            raise HostsFileError(f"Failed to write hosts file: {exc}") from exc

    def _existing_rules(self, lines: List[str]) -> Set[str]:
        rules: Set[str] = set()
        for line in lines:
            if RULE_MARKER in line:
                parts = line.split()
                if len(parts) >= 2:
                    rules.add(parts[1].strip().lower())
        return rules

    # ---------- Public API ----------
    def block(self, domains: Iterable[str], redirect_ip: str = DEFAULT_REDIRECT_IP) -> int:
        """
        Add blocking rules for the given domains. Returns number of new rules added.
        """
        clean_domains = [_normalize_domain(d) for d in domains]
        if not clean_domains:
            return 0

        lines = self._read()
        existing = self._existing_rules(lines)
        added = 0

        for domain in clean_domains:
            if domain in existing:
                continue
            lines.append(BlockRule(domain, redirect_ip).line())
            added += 1

        if added:
            self._write(lines)
        return added

    def unblock(self, domains: Iterable[str]) -> int:
        """
        Remove blocking rules for the given domains. Returns number of rules removed.
        """
        targets = { _normalize_domain(d) for d in domains }
        if not targets:
            return 0

        lines = self._read()
        before = len(lines)
        def keep(line: str) -> bool:
            if RULE_MARKER not in line:
                return True
            parts = line.split()
            return not (len(parts) >= 2 and parts[1].strip().lower() in targets)

        new_lines = [ln for ln in lines if keep(ln)]
        removed = before - len(new_lines)
        if removed:
            self._write(new_lines)
        return removed

    def is_blocked(self, domain: str) -> bool:
        d = _normalize_domain(domain)
        lines = self._read()
        return d in self._existing_rules(lines)

    def list_blocked(self) -> List[str]:
        lines = self._read()
        return sorted(self._existing_rules(lines))
