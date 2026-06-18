# sources/sync-backup/borg/src/borg/__init__.py

## Purpose
This package initializer exposes Borg's version and validates that dynamically generated version metadata is sane. It is imported by runtime CLI code, packaging/build helpers, and callers that need `borg.__version__`.

## Important APIs, Types, and Functions
- Imports `parse` from `packaging.version` and `version` from `._version`.
- Exports `__version__` as the dynamic Borg version string.
- Computes `__version_tuple__` from the parsed release tuple.
- A top-level assertion rejects `0.1.dev...` fallback versions and non-integer release components.

## Control Flow
Importing `borg` immediately imports `_version`, parses the version, and asserts that the result is not the setuptools-scm fallback and has integer semantic-release components. If the assertion fails, import aborts with a detailed message for broken repackaging or missing Git tags/version override.

## State and Persistence Behavior
The module has no persistence and no mutable runtime state beyond module globals. It depends on installation-time/generated `_version.py` content, usually produced by setuptools-scm. Import failure affects all Borg CLI and library entry points.

## Dependencies and Integration Points
It integrates with setuptools-scm version generation, `setup.py`, CLI version display in `archiver/__init__.py`, and package metadata. The assertion message explicitly points maintainers toward correct tags or `SETUPTOOLS_SCM_PRETEND_VERSION`.

## Risks and Edge Cases
- Assertion-based validation can be disabled by optimized Python (`-O`), but Borg's archiver separately refuses to run with assertions disabled.
- Non-standard version schemes may fail if release components are not integers.
- Any missing or malformed `_version.py` makes the whole package unimportable.

## Test Signals
Tests should import `borg`, check `__version__` and `__version_tuple__`, verify `borg --version`, and exercise packaging from Git and sdist contexts. A packaging regression test should cover `SETUPTOOLS_SCM_PRETEND_VERSION` and absence of Git metadata.
