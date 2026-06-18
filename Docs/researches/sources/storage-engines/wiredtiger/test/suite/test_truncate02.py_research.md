<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate02.py

Purpose: Tests fast-delete transactional visibility when truncating leaf pages that are not in memory.

Important APIs/types/functions: `test_truncate_fast_delete` inherits `test_truncate_base`, uses `SimpleDataSet`, `cursor_count`, `outside_count`, `session.truncate`, cursor iteration forward/backward, `reopen_conn`, and isolation modes `read-committed` and `read-uncommitted`.

Control flow: The test creates a large small-page file/layered object, optionally adds overflow records, checkpoints and reopens, optionally reads or writes rows before truncation, then truncates a large middle range inside a transaction. It optionally reads/writes after truncation, checks visibility from the same transaction and separate sessions, and finally commits or rolls back and validates final record counts.

State and persistence behavior: Fast-delete state is stored in page references for pages not in cache. The test covers committed and aborted truncate transaction state, as well as pages forced into memory by overflow, reads, or writes.

Dependencies and integration points: Integrates btree fast-delete, transaction visibility, isolation levels, row/column/string key formats, optional disaggregated layered tables, and overflow item behavior.

Risks: Counts depend on inclusive/exclusive range behavior and isolation semantics. Overflow or prior page instantiation can force slow paths, so scenarios are designed to vary fast-delete eligibility.

Test signals: Forward/backward cursor counts before and after commit/rollback are the main signals, including outside read-committed/uncommitted visibility differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate02.py -->
