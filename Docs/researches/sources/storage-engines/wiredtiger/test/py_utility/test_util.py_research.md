# sources/storage-engines/wiredtiger/test/py_utility/test_util.py

Purpose: bootstraps Python import/library paths for WiredTiger tests so they use the local build tree and bundled third-party test dependencies.

Important APIs and control flow: `get_dist_top_dir()` walks from this file to the distribution root. `find_build_dir()` prefers `WT_BUILDDIR`, then current directory, dist top, and dist top `build`, accepting directories that contain `wt` or `wt.exe`. `setup_wiredtiger_path()` inserts `<build>/lang/python` ahead of installed packages and appends `.libs` to `LD_LIBRARY_PATH` and `DYLD_LIBRARY_PATH` when present. `setup_3rdparty_paths()` scans `test/3rdparty` children for `lib`, `python`, or root package directories. `setup_paths()` runs both setup phases.

State and persistence behavior: mutates `sys.path` and process environment variables. It exits the process if no usable build directory is found.

Dependencies and integration points: imported early by Python test runners before importing `wiredtiger`, `wttest`, or bundled dependencies. It integrates with both in-tree and explicit build-dir workflows.

Risks: build-dir detection can pick the wrong build when multiple builds exist. Path separator logic uses `:`, which is POSIX-oriented. It does not validate ABI compatibility between the Python extension and libraries discovered via environment path.

Test signals: successful import of local `wiredtiger` and third-party modules after `setup_paths()` is the primary signal.
