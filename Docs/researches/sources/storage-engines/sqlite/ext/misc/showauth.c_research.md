# sources/storage-engines/sqlite/ext/misc/showauth.c

Purpose: installs a debug SQLite authorizer callback that prints authorization events and allows them.

Important APIs/types/functions: `authCallback()` maps known authorizer opcodes to names, normalizes null arguments to `"NULL"`, prints `AUTH: op,z1,z2,z3,z4`, and returns `SQLITE_OK`. `sqlite3_showauth_init()` installs it with `sqlite3_set_authorizer()`.

Control flow: loading the extension replaces the connection's current authorizer. SQLite invokes it for DDL, DML, reads, functions, pragmas, transactions, recursive operations, and other authorization checks; all are logged and permitted.

State and persistence: connection-local authorizer registration persists until replaced or cleared; only stdout diagnostics are emitted.

Dependencies/integration: SQLite extension and authorizer APIs plus stdio.

Risks/test signals: overwrites any existing security authorizer, stdout side effects, newer opcode names may fall back to numeric output, and concurrent output may interleave. Test representative statements, null argument formatting, allow-all behavior, and restoring/replacing an existing authorizer.
