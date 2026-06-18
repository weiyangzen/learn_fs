# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.h

Purpose: declares cluster-aware dbwrap open helpers.

Important APIs/types/functions: forward `struct db_context`, `db_is_local(name)`, and `db_open(...)`.

Control flow: callers use `db_is_local()` for routing decisions or call `db_open()` directly to receive either local TDB or CTDB-backed `db_context` based on runtime clustering and per-db configuration.

State and persistence: no public state; returned context owns backend-specific state.

Dependencies/integration: requires dbwrap lock-order enum and flags from surrounding dbwrap private/public includes.

Risks/test signals: API returns null and sets errno for many configuration/runtime failures, so callers need robust error reporting. Compile tests should ensure declarations match implementation and all call sites pass valid lock-order values.
