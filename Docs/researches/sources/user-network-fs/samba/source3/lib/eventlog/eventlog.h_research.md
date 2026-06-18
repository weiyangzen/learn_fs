# sources/user-network-fs/samba/source3/lib/eventlog/eventlog.h

Purpose: defines eventlog TDB metadata keys, database version, and the refcounted `ELOG_TDB` handle.

Important APIs/types/functions: `ELOG_TDB`, `EVT_OLDEST_ENTRY`, `EVT_NEXT_RECORD`, `EVT_VERSION`, `EVT_MAXSIZE`, `EVT_RETENTION`, and database version constants.

Control flow: no runtime flow; consumers use these constants to initialize, validate, prune, and export eventlog databases.

State/persistence behavior: metadata key names are the persistent TDB contract. `ELOG_TDB` is process-local open-handle state.

Dependencies/integration: included by eventlog utility and RPC code.

Risks/test signals: key or version changes affect compatibility. Tests should verify metadata initialization and version mismatch recovery.
