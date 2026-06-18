# sources/security-integrity/selinux/libsemanage/src/database_activedb.c

Purpose: implements a generic active-state database backend using the linked-list cache machinery plus record-specific read and commit callbacks.

Important APIs/types/functions: `dbase_activedb_cache`, `dbase_activedb_flush`, `dbase_activedb_init`, `dbase_activedb_release`, and `SEMANAGE_ACTIVEDB_DTABLE`.

Control flow: cache calls the record active table's `read_list`, prepends each returned record into the linked-list cache, frees the temporary array, and records the current serial. Flush lists cached records and calls `commit_list`, then clears the modified flag.

State and persistence behavior: caches active records in memory; flush writes the active backend's complete list to runtime state. There is no file path or policydb persistence in this generic layer.

Dependencies and integration points: depends on `database_llist` for CRUD/list/cache management and a `record_activedb_table_t` supplied by object-specific code such as active booleans.

Risks: full-list flush semantics can lose concurrent active changes. Test signals include cache load, modify then flush, drop/reload, and cleanup on partial cache failures.
