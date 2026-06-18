<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema09.py

Purpose: regression test for recovery cleanup of incomplete table metadata left by crashes at precise schema create/drop points.

Important APIs/types/functions: `test_schema09` extends `WiredTigerTestCase` and `suite_subprocess`; it uses `conn.reconfigure` with `debug_mode=(crash_point=...)`, subprocess function execution, metadata cursors, `wiredtiger.WT_NOTFOUND`, and `expectedStdoutPattern`. Hooks skip tiered and disaggregated storage.

Control flow: close the main connection, run a subprocess that enables one crash point and performs create or drop expected to crash, reopen the resulting home and expect "removing incomplete table", disable the crash point, verify file/table/colgroup metadata entries are gone, assert open/drop fail, then create and drop the same table successfully.

State and persistence behavior: the test relies on log-enabled recovery and deliberately inconsistent metadata involving table, file, and colgroup entries. Recovery must force-drop incomplete schema artifacts before normal use resumes.

Dependencies/integration points: integrates debug crash points, subprocess isolation, metadata cursor lookup, recovery messages, and schema APIs. Risks include crash-point names and stdout text coupling; signals are metadata absence after recovery and successful recreate/drop lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema09.py -->
