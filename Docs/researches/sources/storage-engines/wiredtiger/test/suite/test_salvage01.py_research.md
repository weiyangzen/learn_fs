<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage01.py

Purpose: verifies WiredTiger salvage through both the `wt salvage` utility and the Python API, for empty, healthy, and intentionally damaged row-store and variable-length column-store files.

Important APIs/types/functions: `test_salvage01` extends `WiredTigerTestCase` and `suite_subprocess`; helpers include `moreinit`, key/value generators, `populate`, `check_populate`, `check_damaged`, `damage_inner`, `runWt`, `session.salvage`, `salvageUntilSuccess`, and `session.verify`. Scenarios cover string row keys, record-number column keys, and optional `failpoint_eviction_split` timing stress.

Control flow: each test creates `table:test_salvage01.a`, optionally populates 1000 records with one unique corruption target, runs salvage in-process or via subprocess, and revalidates contents. Damaged tests close the connection, modify the `.wt` file byte matching the unique string, reopen with prefetch disabled, confirm verify reports checksum damage, then salvage and accept a partial but internally consistent table.

State and persistence behavior: damage is performed directly on the persisted table file after clean close, so salvage must rebuild from disk structures rather than in-memory state. VLCS uses small pages to avoid losing the entire table to one-page corruption.

Dependencies/integration points: covers file naming, table/file URI differences, external `wt`, stdout/stderr filtering, checksum detection, and prefetch interaction. Risks include brittle byte searching, page-size sensitivity, and partial salvage expectations; test signals are no error output for clean salvage, full record preservation for undamaged data, and at least some correct records after repair.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage01.py -->
