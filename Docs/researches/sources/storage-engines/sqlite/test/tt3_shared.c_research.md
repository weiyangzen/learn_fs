## sources/storage-engines/sqlite/test/tt3_shared.c

### Purpose
`tt3_shared.c` adds `shared1`, a minimal shared-cache connection churn test. It repeatedly opens connections and scans a simple table from multiple threads.

### Important APIs, types, and functions
`shared_thread1()` loops until timeout, opening `test.db`, running `SELECT * FROM t1`, and closing. `shared1()` creates `t1`, enables shared cache, launches five `shared_thread1` workers, joins them, and disables shared cache.

### Control flow
The setup is intentionally small: create an empty table, then run concurrent open/select/close cycles for the configured duration. All error handling is delegated to the `threadtest3` wrappers.

### State and persistence behavior
`test.db` contains only table `t1`, and no worker modifies it. The test is about shared-cache lifecycle state and schema access under concurrent connection churn.

### Dependencies and integration points
This file depends on `threadtest3` infrastructure and SQLite shared-cache support. It is included into the `threadtest3` executable.

### Risks and test signals
Because there are no writes, this test mostly detects shared-cache open/close, schema, and reference-counting regressions. Signals are five `done!` thread results and no global errors.
