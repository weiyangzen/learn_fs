## sources/storage-engines/sqlite/test/tt3_lookaside1.c

### Purpose
`tt3_lookaside1.c` adds `lookaside1`, a shared-cache race probe focused on lookaside allocation and statement finalization while readers and a writer operate concurrently.

### Important APIs, types, and functions
`lookaside1_thread_reader()` prepares `SELECT 1 FROM t1`, steps through rows, and inside the loop runs a second query over `t2`, then checks finalize errors. `lookaside1_thread_writer()` repeatedly updates `t3` inside a rolled-back transaction. `lookaside1()` creates the schema and launches five readers plus one writer.

### Control flow
Setup builds two `WITHOUT ROWID` tables and a small blob table. Readers repeatedly prepare, step, execute nested SQL through the harness, and finalize. The writer loops on `BEGIN`, `UPDATE`, `ROLLBACK` until timeout. Shared cache is enabled only for the test body.

### State and persistence behavior
`test.db` contains `t1`, `t2`, and `t3`. The writer rolls back all updates, so persistent logical state should remain stable. The test stresses connection-local statement and lookaside state rather than durable data changes.

### Dependencies and integration points
The file depends on `threadtest3` infrastructure, shared-cache mode, SQLite lookaside behavior, `WITHOUT ROWID` handling, and prepared statement finalization semantics.

### Risks and test signals
The expected failure mode is a race surfacing as prepare/step/finalize or lock errors. Since the writer rolls back, data validation is minimal. Signals are clean reader/writer `ok` summaries and no finalize errors reported through `sqlite_error()`.
