# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.h

Purpose: declares the CTDB dbwrap backend entry points.

Important APIs/types/functions: forward declarations for `struct db_context` and `struct ctdbd_connection`; `db_open_ctdb()` and `ctdb_async_ctx_reinit()`.

Control flow: `db_open()` and cluster-aware callers invoke `db_open_ctdb()` to attach/open a CTDB-backed database. Messaging or reconnect paths can call `ctdb_async_ctx_reinit()` to rebuild the process-global async CTDB connection after fork or connection loss.

State and persistence: no public state; implementation manages local TDB copies, CTDB db IDs, transaction state, and async connection state.

Dependencies/integration: includes talloc and `dbwrap_private.h` for lock order and dbwrap flags.

Risks/test signals: callers must only use this when clustering and messaging CTDB are initialized. Header tests should validate prototypes remain consistent with `dbwrap_open.c`, `ctdb_dummy.c`, and `dbwrap_ctdb.c` in both clustered and non-clustered builds.
