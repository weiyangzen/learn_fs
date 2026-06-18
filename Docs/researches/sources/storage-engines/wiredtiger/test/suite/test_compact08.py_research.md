# sources/storage-engines/wiredtiger/test/suite/test_compact08.py

Purpose: verifies compaction is not allowed for in-memory or read-only databases.

Important APIs and types: `session.compact`, `reopen_conn(config="in_memory=true")`, `reopen_conn(config="readonly=true")`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: create a file, reopen as in-memory and check foreground compaction prints unsupported message while background compaction raises with a specific warning; reopen read-only and verify compaction attempts raise operation-not-supported errors.

State and persistence behavior: this is API guard behavior, not data mutation. It ensures compaction does not run against configurations where rewriting files is impossible or invalid.

Dependencies and integration points: connection mode flags, foreground/background compaction API paths, and stdout/error message contracts.

Risks: final background read-only check calls `start_foreground_compaction` again, likely a copy/paste mistake, so the background path in read-only mode is not actually exercised.

Test signals: in-memory foreground warning observed, in-memory background raises, and read-only compact raises operation-not-supported.
