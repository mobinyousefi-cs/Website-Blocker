#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Website Blocker
File: exceptions.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-05
Updated: 2025-10-05
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Custom exception hierarchy for the Website Blocker.
"""

class HostsPermissionError(PermissionError):
    """Raised when the process lacks permission to modify the hosts file."""

class HostsFileError(RuntimeError):
    """Raised when the hosts file cannot be read or written."""

class InvalidDomainError(ValueError):
    """Raised when a provided domain/URL is syntactically invalid."""
