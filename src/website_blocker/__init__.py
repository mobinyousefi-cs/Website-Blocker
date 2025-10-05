#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Website Blocker
File: __init__.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Package initializer for the Website Blocker. Exposes high-level API and version.
"""

from ._version import __version__
from .hosts_manager import HostsManager, BlockRule, DEFAULT_REDIRECT_IP
