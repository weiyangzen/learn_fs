# sources/storage-engines/wiredtiger/test/py_install/testbase.py

Purpose: installation sanity test for the Python `wiredtiger` package after `pip install wiredtiger`. It verifies that the extension imports, opens a home, performs basic table operations, and exposes version information.

Important APIs and control flow: imports `wiredtiger_open` and `wiredtiger_version`, recreates `WTPY_TEST`, opens a connection with `create`, creates `table:foo` with string keys and integer values, writes three records through a cursor mapping interface, verifies key `B` returns `200`, closes handles, prints the version, and reports success.

State and persistence behavior: deletes and recreates local directory `WTPY_TEST`, then persists a small WiredTiger table there. It does not clean up after success, leaving the home for inspection.

Dependencies and integration points: depends on the installed Python package and its native library resolution, not the local test path setup utilities. This is useful for packaging/installation validation.

Risks: uses a fixed relative directory name, so concurrent runs in one working directory can collide. It only checks a minimal cursor path and will not catch most optional-package issues.

Test signals: failure raises an exception on incorrect lookup; success prints `testbase success.` and the WiredTiger version tuple/string.
