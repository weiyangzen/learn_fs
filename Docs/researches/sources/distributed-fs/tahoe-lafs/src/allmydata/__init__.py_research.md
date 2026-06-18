# sources/distributed-fs/tahoe-lafs/src/allmydata/__init__.py

## Purpose

This package initializer exposes Tahoe-LAFS version metadata, applies third-party monkey patches, and configures BytesWarning handling for allmydata modules.

## Important APIs, Types, And Functions

`__all__` exports version and app-name symbols. `__version__`, `full_version`, and `branch` default to `"unknown"` and are optionally imported from generated `allmydata._version`. `__appname__` is `tahoe-lafs`, and `__full_version__` combines the app name with `__version__`. The module imports and calls `._monkeypatch.patch()`, then installs a warnings filter that turns `BytesWarning` into errors for modules matching `.*allmydata.*`.

## Control Flow

Importing `allmydata` attempts to import generated version values twice, tolerating `ImportError`. It computes `__full_version__`, applies monkey patches, deletes the local patch binding, and updates the warnings filter.

## State And Persistence

State is module-global version metadata and process-global warning filter state. There is no on-disk persistence from this file.

## Dependencies And Integration Points

It integrates with hatch-vcs-generated `_version.py`, application version announcements in client code, and any monkey-patches needed before the rest of Tahoe imports third-party libraries.

## Risks

Import-time side effects affect the whole process. Missing `_version.py` produces `"unknown"` metadata, which can weaken diagnostics and peer version reporting. Turning BytesWarnings into errors can surface only under `python -b`, so production/test differences remain possible.

## Test Signals

Import `allmydata` with and without `_version.py`, verify exported version strings, and run tests under `python -b` to ensure allmydata BytesWarnings fail as intended.
