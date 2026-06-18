# sources/sync-backup/borg/MANIFEST.in Research

## Purpose

`MANIFEST.in` customizes BorgBackup source distribution contents. Because `setuptools_scm` includes git-committed files automatically, this file mostly excludes unneeded repository metadata and explicitly includes platform C source files.

## Important APIs, Types, and Functions

Directives include `exclude` for `.editorconfig`, `.gitattributes`, `.gitignore`, `.mailmap`, and `Vagrantfile`; `prune .github`; and `include` for platform-specific C files under `src/borg/platform/`.

## Control Flow

During sdist creation, setuptools applies these manifest rules on top of setuptools-scm's file discovery. The `.github` tree is omitted, while selected C files are retained.

## State and Persistence Behavior

This file affects package build artifacts only. It does not affect installed runtime behavior directly except by determining which source files are available in sdists.

## Dependencies and Integration Points

It integrates with `pyproject.toml`, `setup.py`/build backend behavior, setuptools-scm, and platform extension compilation. Development docs explicitly remind maintainers to verify `MANIFEST.in`, `pyproject.toml`, and setup metadata before release.

## Risks and Edge Cases

If new required generated or platform files are added and not committed or included, sdist builds can fail. Pruning `.github` is expected but removes workflow metadata from source archives. Comments imply setuptools-scm handles most committed files, so maintainers may overlook explicit include needs for unusual build inputs.

## Test Signals

Run `python -m build`, inspect the sdist file list, and install/test from the sdist rather than the git checkout. Release checks should verify platform C files are present.
