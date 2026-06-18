# sources/user-network-fs/samba/source3/lib/serverid.c

## Purpose
This file implements reliable `serverid_exists()` checks for local and clustered Samba server IDs.

## Important APIs, Types, And Functions
`serverid_exists_local()` first checks PID existence, then optionally verifies the `unique_id` through `messaging_dgm_get_unique()` unless the ID requests no verification. `serverid_exists()` dispatches to local checks for local proc IDs, to CTDB process existence when clustering is enabled, and otherwise returns false for nonlocal IDs.

## Control Flow
Local control flow is conservative: if the process exists and unique-id lookup fails with `EACCES`, the code logs and assumes the process still exists. Other unique-id lookup failures return false. Clustered flow uses `ctdbd_process_exists()` through the messaging CTDB connection.

## State And Persistence
The file does not persist state. It observes process state, messaging datagram lock/unique-id state, and CTDB cluster process state.

## Dependencies And Integration Points
It depends on process existence helpers, procid locality checks, loadparm clustering, CTDB messaging, and datagram messaging unique IDs. It is used by server-id databases, watchers, and cleanup code to avoid stale process references.

## Risks And Test Signals
Risks are PID reuse without unique-id verification, permission-denied false positives, CTDB connectivity failures, and nonlocal IDs when clustering is disabled. Tests should cover local pid exists/dead, unique-id match/mismatch/not-to-verify, `EACCES` behavior, and clustered vs nonclustered dispatch.
