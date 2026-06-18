## sources/storage-engines/sqlite/test/tt3_index.c

### Purpose
`tt3_index.c` adds `create_drop_index_1` to `threadtest3`, stressing concurrent index DDL and ordered reads in shared-cache mode.

### Important APIs, types, and functions
`create_drop_index_thread()` repeatedly opens `test.db`, drops four indexes if present, recreates them, selects rows ordered by each indexed column, clears expected `SQLITE_LOCKED`, and closes. `create_drop_index_1()` initializes table `t11`, enables shared cache, launches five worker threads, then disables shared cache.

### Control flow
Setup creates `t11(a,b,c,d)` and fills it with 100 rows. Workers run until the shared stop time expires. Each iteration performs DDL churn and read queries from a fresh connection.

### State and persistence behavior
The only persistent state is `test.db`, table `t11`, and transient indexes `i1` through `i4`. Indexes may exist or be absent depending on the exact interleaving when the test ends.

### Dependencies and integration points
The file depends entirely on `threadtest3` helper macros, `sqlite3_enable_shared_cache()`, and SQLite schema-lock behavior. It is included by `threadtest3.c`.

### Risks and test signals
`SQLITE_LOCKED` is expected and cleared, so unexpected schema or corruption failures are the important signal. A successful run prints worker `ok` messages and no global errors. This test is sensitive to shared-cache behavior and DDL lock acquisition changes.
