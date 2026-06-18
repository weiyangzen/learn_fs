<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate05.py

Purpose: Ensures truncating at a read timestamp older than a newer committed update fails rather than deleting over invisible newer data.

Important APIs/types/functions: `test_truncate05` uses small cache config, `session.truncate`, timestamped commits, `reopen_conn`, large insert workload for eviction pressure, and expected `WiredTigerError`.

Control flow: The test inserts keys 1-999 at timestamp 2, reopens to force content to disk, updates key 500 at timestamp 3, inserts many more keys at timestamp 4 to pressure eviction, begins a read transaction at timestamp 2, then attempts to truncate keys 1-1000 and expects failure.

State and persistence behavior: The key state is a newer update not visible to the truncating transaction. The test forces eviction/disk state so truncate must inspect or protect against unseen newer history.

Dependencies and integration points: Integrates timestamp read visibility, truncate conflict detection, eviction pressure, and row/column store formats.

Risks: If truncate ignores newer invisible updates, it can corrupt history by deleting data outside the reader's snapshot.

Test signals: The truncate call must raise `WiredTigerError`; rollback then cleans the read transaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate05.py -->
