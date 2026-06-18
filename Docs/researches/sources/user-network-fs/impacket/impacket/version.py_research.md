# sources/user-network-fs/impacket/impacket/version.py

## Purpose

`version.py` centralizes runtime version presentation for Impacket. It reads installed package metadata, builds banner strings, and exposes the package installation path.

## Important APIs, Types, And Functions

The module defines `version`, `BANNER`, `DEPRECATION_WARNING_BANNER`, and `getInstallationPath()`. It imports `importlib.metadata.version` as `get_version`, catches `PackageNotFoundError`, and reads `impacket.__path__`.

## Control Flow

At import time it calls `get_version('impacket')`. If metadata is missing, it sets `version = "?"` and prints a source-tree hint. `BANNER` is formatted from the chosen version. `getInstallationPath()` returns `__path__[0]` in a display string.

## State And Persistence Behavior

There is no persistence. State is import-time module globals. The fallback path prints to stdout during import, which can affect tools or tests.

## Dependencies And Integration Points

It depends on Python package metadata and the `impacket` package path. Impacket examples and command-line tools use the banner and installation-path helper for startup and diagnostics.

## Risks And Edge Cases

Source checkouts without metadata report `"?"`. Import-time printing is noisy for library consumers. `getInstallationPath()` assumes `__path__` has at least one entry.

## Test Signals

Tests should mock metadata success and `PackageNotFoundError`, verify banner formatting, confirm fallback behavior, and assert installation path reporting from a controlled package path.
