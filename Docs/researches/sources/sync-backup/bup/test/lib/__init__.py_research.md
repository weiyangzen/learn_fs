# sources/sync-backup/bup/test/lib/__init__.py

Purpose: empty package marker for the bup test support library directory.

Important APIs/types/functions: no imports, exports, functions, classes, or runtime statements are defined.

Control flow: none. Importing this package performs no work.

State and persistence behavior: no state, side effects, or persistence behavior.

Dependencies/integration points: enables Python package-style imports from `test/lib` when the test harness places it on `PYTHONPATH`, including modules such as `buptest` and `wvpytest`.

Risks and test signals: behavior depends only on file presence. Any future code added here would become import-time behavior for the entire test suite and should be kept minimal.
