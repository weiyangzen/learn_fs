<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config05.py

Purpose: tests multiple connection/session open constraints, session limits, exclusive create, and duplicate database management.

Important APIs and control flow: default setup is disabled so each test opens explicitly. Helpers populate and verify a simple string table. Tests cover normal single connection, `session_max=1`, exhausting sessions to produce `out of sessions`, `create,exclusive` followed by exclusive reopen failure, and opening the same home with `create` while another connection manages it.

State, persistence, and dependencies: state is a simple table in the WiredTiger home and one or two connection handles tracked by `close_conn()`. Dependencies are `wiredtiger`, `wttest`, session open/close, table creation, and cursor iteration.

Integration points: targets connection lifecycle management, session pool limits, exclusive home locking/metadata rules, and duplicate-open protection.

Risks and test signals: the session exhaustion test is skipped for tiered storage. Some tests intentionally leave the primary connection open to validate management conflicts. Pass signals are precise errors for too many sessions, existing database with exclusive open, and already-managed homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config05.py -->
