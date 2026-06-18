# sources/distributed-fs/tahoe-lafs/src/allmydata/util/assertutil.py

## Purpose

This is a compatibility shim that re-exports assertion helpers from `pyutil.assertutil`. Older Tahoe-LAFS code imports `_assert`, `precondition`, and `postcondition` from this local module, so this file keeps those import paths stable.

## APIs and control flow

The public API is exactly `_assert`, `precondition`, and `postcondition`, listed in `__all__`. There is no custom control flow, validation, state, or persistence here. All behavior belongs to the upstream `pyutil.assertutil` implementations.

## State, dependencies, risks, and tests

The only dependency is `pyutil.assertutil`. The risk is compatibility drift: if the pyutil helpers change message formatting, exception behavior, or availability, Tahoe modules that rely on rich assertion diagnostics will observe that behavior through this shim. Removing this file would break many local imports.

Test signals are import-level and behavioral: callers should be able to import the three names, failed preconditions should include useful diagnostic kwargs, and modules such as `uri.py`, `base32.py`, `encodingutil.py`, and `fileutil.py` should continue to use the same assertions without local changes.
