# sources/user-network-fs/samba/source3/smbd/conn_idle.c

## Purpose
`conn_idle.c` detects fully idle server connections and implements asynchronous forced tree disconnect for shares, waiting for outstanding AIO before disconnecting tree connections and reloading services.

## Important APIs, types, and functions
- `conn_idle_all()` updates last-used timestamps and returns true only when every connection has no open files and exceeds `deadtime`.
- `conn_force_tdis()` scans tree connections and starts an async forced disconnect for those accepted by a caller-supplied predicate.
- `conn_force_tdis_send()` marks a TCON as `NT_STATUS_NETWORK_NAME_DELETED`, marks associated FSPs closing, and queues waiters behind any outstanding AIO.
- `conn_force_tdis_done()` disconnects the SMBX TCON, frees it, switches to root, and reloads services.

## Control flow
Idle detection uses `lastused_count` as an activity counter: if it changed, the connection's `lastused` timestamp is refreshed. Forced disconnect is deliberately asynchronous. The TCON is marked unusable first so no new request should attach to it. Existing FSPs for that connection are marked closing, and if they have AIO, the code waits on a per-request `tevent_queue`. A final waiter at the end of the queue fires when all prior AIO waiters are gone, then `smbXsrv_tcon_disconnect()` performs the actual tree disconnect.

## State and persistence behavior
State is mostly in-memory TCON/FSP status plus SMBX TCON database updates performed by `smbXsrv_tcon_disconnect()`. Service reload after disconnect can refresh in-memory loadparm state. The async request is allocated on the NULL context and freed in completion.

## Dependencies and integration points
The file depends on tevent queues, SMBX TCON state, AIO request destructors, FSP lists, `change_to_root_user()`, and `reload_services()`. It is triggered by message handlers in `conn_msg.c` and by idle/deadtime server logic.

## Risks and edge cases
- Forced disconnect must prevent new I/O before waiting for old AIO; otherwise FSP close can race with new operations.
- `conn_force_tdis_done()` stores `tcon` before disconnect and sets `conn = NULL`, so later code must not dereference the freed connection.
- Service reload explicitly disables reload caching to avoid repeated-call suppression.
- Idle detection returns false as soon as one connection is active or has open files.

## Test signals
Tests should simulate no-deadtime, active-file, and all-idle cases; force-disconnect shares with and without AIO; verify TCON status changes reject new operations; and verify service reload after disconnect.
