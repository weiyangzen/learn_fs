# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.c

Purpose: central database opener that chooses local TDB or clustered CTDB dbwrap backend and applies per-database tuning.

Important APIs/types/functions: `db_is_local()` and `db_open()`.

Control flow: `db_is_local()` checks clustering, CTDB socket existence, strips path to basename, and honors `ctdb:<db>` parameter overrides. `db_open()` validates lock order, applies `tdb_hash_size:<base>`, readonly optimization for clear-if-first DBs, TDB mutex options subject to mmap and robust mutex availability, then chooses CTDB if clustering is enabled and allowed. CTDB path initializes global messaging, verifies a CTDB connection, and delegates to `db_open_ctdb()`. Otherwise it initializes loadparm context and calls `dbwrap_local_open()`.

State and persistence: no owned persistent state; returns a `db_context` backed by either CTDB/local TDB. It modifies local `tdb_flags/dbwrap_flags` based on configuration.

Dependencies/integration: loadparm, cluster support socket helper, messages CTDB, global contexts, CTDB connection, local/CTDB dbwrap backends, TDB runtime mutex checks.

Risks/test signals: clustered configuration with missing socket returns null; CTDB open failure sets `errno` to EIO if unset. Mutex requirements can force flags even when runtime support is absent. Tests should cover local fallback, per-DB CTDB disable, missing socket, global messaging failure, robust mutex unavailable, mmap disabled, readonly optimization toggles, and invalid lock order.
