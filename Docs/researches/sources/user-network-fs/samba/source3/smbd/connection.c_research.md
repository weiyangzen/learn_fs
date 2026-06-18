# sources/user-network-fs/samba/source3/smbd/connection.c

## Purpose
`connection.c` counts active tree connections for a share using Samba's global SMBX TCON database and exposes a service-number based "in use" check for reload logic.

## Important APIs, types, and functions
- `count_current_connections(sharename, verify)` traverses `smbXsrv_tcon_global.tdb` and counts entries whose `share_name` matches.
- `connections_snum_used()` maps a service number to its configured service name and returns whether any verified current connection uses it.
- `count_fn()` optionally filters dead server IDs with `process_exists()`.

## Control flow
The count path initializes a `count_stat`, traverses all global TCON records with `smbXsrv_tcon_global_traverse()`, and increments for matching share names. The comment explicitly accepts a race rather than chain-locking first because locking would risk deadlock.

## State and persistence behavior
The file reads global TCON database state but does not write it. Returned counts are snapshots and can be stale immediately due to concurrent connect/disconnect.

## Dependencies and integration points
It depends on SMBX TCON global traversal, server ID liveness checks, loadparm service-name substitution, and service reload code. It is distinct from `conn_snum_used()` in `conn.c`, which only checks the current server process.

## Risks and edge cases
- Counting without pre-locking is intentionally racy.
- Traversal failure logs at level 0 and returns zero, which may make reload logic think a share is unused.
- `verify=true` trades accuracy for process liveness checks and may ignore stale database records.

## Test signals
Useful tests create multiple TCON records for one share, include dead server IDs, check `verify` behavior, simulate traversal errors, and compare global count behavior with current-process `conn_snum_used()`.
