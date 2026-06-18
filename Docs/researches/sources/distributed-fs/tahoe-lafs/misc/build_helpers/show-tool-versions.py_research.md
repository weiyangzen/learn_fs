# sources/distributed-fs/tahoe-lafs/misc/build_helpers/show-tool-versions.py

## Purpose

This diagnostic script prints platform, Python, locale, compiler/tool, and selected Python package versions for build logs.

## Important APIs, Types, and Functions

`foldlines` collapses multi-line command output. `print_platform`, `print_python_ver`, and `print_python_encoding_settings` report interpreter and locale metadata. `print_stdout` runs an external command and prints a compact label. `print_as_ver` handles assembler version probing while avoiding clobbering an existing `a.out`. `print_setuptools_ver` and `print_py_pkg_ver` use `importlib.metadata.version` and optional module imports.

## Control Flow

The script runs all print helpers at import/execution time in a fixed order. Missing external commands are reported as "no such file or directory"; other `EnvironmentError`s print tracebacks but the script continues.

## State, Dependencies, Integration, Risks, and Tests

State is stdout/stderr logging and possible deletion of `a.out` only if the assembler creates it. Dependencies are many external tools (`virtualenv`, `tox`, `gcc`, `git`, `openssl`, etc.) and Python package metadata. Integration is CI/buildbot environment capture. Risks include stale package list, duplicate `cryptography` entry, command hangs because no timeout is used, and deprecated `locale.getdefaultlocale`. Tests should monkeypatch `subprocess.Popen` and metadata lookups to verify missing commands, multi-line folding, and PackageNotFound behavior.
