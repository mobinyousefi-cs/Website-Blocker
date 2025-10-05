#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for HostsManager using a temporary hosts file (no admin needed).
"""

from pathlib import Path
import tempfile

import pytest

from website_blocker.hosts_manager import HostsManager, DEFAULT_REDIRECT_IP
from website_blocker.exceptions import InvalidDomainError

BASE_HOSTS = """127.0.0.1 localhost
::1 localhost
"""

def make_temp_hosts(initial: str = BASE_HOSTS) -> Path:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    p = Path(tmp.name)
    p.write_text(initial, encoding="utf-8")
    return p

def read_file(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def test_block_and_list():
    hosts_path = make_temp_hosts()
    hm = HostsManager(hosts_path=hosts_path)
    assert hm.list_blocked() == []
    added = hm.block(["example.com", "www.test.org"])
    assert added == 2
    blocked = hm.list_blocked()
    assert "example.com" in blocked and "www.test.org" in blocked
    text = read_file(hosts_path)
    assert "example.com" in text and DEFAULT_REDIRECT_IP in text

def test_idempotent_block():
    hosts_path = make_temp_hosts()
    hm = HostsManager(hosts_path=hosts_path)
    hm.block(["example.com"])
    hm.block(["example.com"])  # no duplicates
    assert hm.list_blocked().count("example.com") == 1

def test_unblock():
    hosts_path = make_temp_hosts()
    hm = HostsManager(hosts_path=hosts_path)
    hm.block(["example.com", "site.net"])
    removed = hm.unblock(["example.com"])
    assert removed == 1
    assert "example.com" not in hm.list_blocked()
    assert "site.net" in hm.list_blocked()

def test_invalid_domain():
    hosts_path = make_temp_hosts()
    hm = HostsManager(hosts_path=hosts_path)
    with pytest.raises(InvalidDomainError):
        hm.block(["http://"])
