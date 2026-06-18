# sources/user-network-fs/samba/source3/utils/net_g_lock.c

Purpose: exposes Samba `g_lock` functionality for diagnostics and command execution under a lock.

Important APIs/types/functions: `net_g_lock()` dispatches `do`, `locks`, `dump`, and `dumpall`. `net_g_lock_init()` creates tevent, messaging, and lock contexts. `net_g_lock_do()` locks and runs a shell command. Dump helpers print owners, keys, and stored lock data.

Control flow: diagnostic commands initialize contexts, read lock names/tables with `g_lock_locks_read()` or `g_lock_dump()`, print data, and free contexts. `do` parses lock name, timeout, and command, acquires a write lock with `g_lock_lock()`, calls `system()`, unlocks, and returns the raw command status.

State and persistence: creates transient lock records in the g_lock backend and can mutate arbitrary system state via the shell command. Dump/list are read-only.

Dependencies/integration: depends on `g_lock.h`, messaging, tevent, server ID formatting, util TDB dumping, and `net_run_function()`.

Risks: `system()` executes caller-supplied shell text. Return value is raw wait status. Timeout uses `atoi()` and millisecond splitting. Locks may remain if the process is killed before unlock.

Test signals: competing lock acquisition; timeout bounds; command return mapping; read/write holder dumps; context init failures; shell quoting cases.
