# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/pyproject.toml

## Purpose

`pyproject.toml` declares the PEP 517 build backend and local Ruff formatting/linting defaults for the vendored `python-subunit` package.

## Important APIs, Types, and Functions

The `[build-system]` table requires `setuptools>=43.0.0` and selects `setuptools.build_meta`, so modern build frontends can build wheels/sdists without invoking `setup.py` directly. The `[tool.ruff]` section sets `line-length = 120` and `target-version = "py37"`, documenting the intended Python syntax baseline for linting.

## Control Flow

Build tools read this file before isolation and dependency installation. The backend then delegates metadata and file selection to setuptools configuration and package files. Ruff reads its section only when linting this sub-tree.

## State and Persistence Behavior

The file persists build-environment requirements and style configuration. It carries no application state and has no runtime effect after the package is installed.

## Dependencies and Integration Points

It integrates with `setuptools`, the local `setup.py`/`setup.cfg` metadata, and any CI or developer lint task that runs Ruff. In the larger WiredTiger tree it is third-party metadata, so repository-wide tooling should avoid rewriting it unless intentionally updating the vendored package.

## Risks and Test Signals

The build backend is stable, but the low minimum setuptools version can interact poorly with newer packaging standards if metadata changes elsewhere. Test signals are successful isolated builds, successful editable or wheel installs, and Ruff invocations honoring Python 3.7-compatible syntax rather than assuming a newer language level.
