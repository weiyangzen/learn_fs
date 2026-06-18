# sources/sync-backup/borg/src/borg/__main__.py

## Purpose
This module is the `python -m borg` entry point. It performs a Windows-specific DLL search path workaround, imports the top-level CLI `main`, and executes it.

## Important APIs, Types, and Functions
- Uses `sys.platform.startswith("win32")` to detect Windows.
- Builds a PATH prefix from `sys.path` entries containing a `DLLs` component.
- Imports `main` via absolute `from borg.archiver import main`, which is explicitly needed for PyInstaller binaries.
- Calls `main()` unconditionally at module import/execution time.

## Control Flow
On Windows, the module prepends discovered DLL directories to `os.environ["PATH"]` so bundled `libcrypto` can be loaded. On all platforms, it imports and calls `borg.archiver.main()`, transferring control to argument parsing, logging setup, signal handling, and command dispatch.

## State and Persistence Behavior
The module mutates only the current process environment by changing `PATH` on Windows. It persists no Borg repository/cache state. Because it calls `main()` at top level, importing `borg.__main__` for introspection can execute the CLI.

## Dependencies and Integration Points
It depends on `sys`, `os`, and `borg.archiver.main`. It integrates with Python's `-m` entry point mechanism, PyInstaller packaging, and Windows Python DLL layout.

## Risks and Edge Cases
- PATH mutation prepends all `sys.path` entries with a `DLLs` component, which can change DLL resolution order.
- If no DLL paths are found on Windows, it still prepends an empty string plus path separator, which may have subtle PATH semantics.
- Top-level execution makes import-time side effects expected but important.

## Test Signals
Test `python -m borg --version` on supported platforms, especially Windows bundled builds. A unit-level smoke test can monkeypatch `sys.platform`/`sys.path` and assert PATH construction. PyInstaller tests should verify the absolute import works.
