# sources/storage-engines/wiredtiger/tools/py_common/wiredtiger_util.py

Purpose: locates and imports the built WiredTiger Python extension for scripts that need `wiredtiger_open`.

Important APIs and control flow: `setup_python_path()` walks upward from the current working directory until it finds a built `wt` or `wt.exe`, then inserts `<build>/lang/python` into `sys.path`; if no build root is found it prints an error and exits. `import_wiredtiger()` first tries `from wiredtiger import wiredtiger_open`, falls back to `setup_python_path()`, then retries. Module import binds the exported name `wiredtiger_open`.

State and persistence behavior: mutates process-global `sys.path` and may terminate the process. It does not write files or database state.

Dependencies and integration points: intended for Python tools run from a WiredTiger build directory. It integrates with the generated/built `wiredtiger` Python module under `lang/python`.

Risks: import-time side effects mean merely importing this module can exit the process. The build-root search is based on `os.getcwd()`, not the script location. Inserting at index 1 may interact with other path entries in surprising ways.

Test signals: no direct tests are present. Practical validation is importing from both a configured Python path and a build directory where `wt` exists.
