# sources/security-integrity/selinux/libsemanage/src/database.c

Purpose: provides generic public-facing database wrappers that enforce initialization, cache entry, and read/write transaction mode before dispatching to backend method tables.

Important APIs/types/functions: internal `assert_init`, `enter_ro`, `exit_ro`, and `enter_rw`; exported wrappers `dbase_modify`, `dbase_set`, `dbase_del`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, and `dbase_list`.

Control flow: write wrappers enter read-write mode, which implicitly begins a transaction, caches the backend, and dispatches. Read wrappers enter read-only mode, cache the backend, dispatch, and then call `semanage_exit_read_lock`.

State and persistence behavior: wrapper calls can populate backend caches and mark them modified through backend operations. Actual persistence occurs later via backend flush during commit.

Dependencies and integration points: sits between every object-specific API and file/policydb/active/join backends. Relies on handle transaction/read-lock helpers and `dbase_config_t` method tables.

Risks: incorrect dconfig initialization is fatal to all callers. Iteration has documented reentrancy restrictions. Test signals include implicit transaction start for writes, read lock balancing on errors, cache refresh behavior, and generic error propagation.
