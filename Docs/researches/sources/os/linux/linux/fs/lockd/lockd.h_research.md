# File Research: sources/os/linux/linux/fs/lockd/lockd.h

Purpose: Central internal lockd header defining debug flags, core host/request/file/block/share structures, status constants, function prototypes, and inline helpers.

Key definitions:
- Debug facility flags and default version/timeout constants.
- Internal status codes that must not be placed on the wire.
- `struct nlm_host` for client/server peer state, RPC client, recovery, lockowners, granted/reclaim lists, NSM handle, namespace, and credentials.
- `struct nsm_handle`, `struct nlm_lockowner`, `struct nlm_wait`, `struct nlm_rqst`, `struct nlm_file`, and `struct nlm_block`.
- Global externs for RPC programs, server versions, grace period, timeout, NSM state, and retry timer.
- Prototypes for client, host, monitor, server lock, file, share, and resource operations.
- Inline helpers for sockaddr access, privileged requester checks, lock comparison, and NLMv4 range conversion.

Dependencies and integration:
- Pulls in protocol declarations from `nlm.h`, generated/user-facing bind headers, and lockd XDR headers.
- Shared by nearly every lockd implementation file.

Risk notes:
- Struct fields encode many lifetime relationships: host refs, lockowner refs, granted/reclaim lists, RPC task refs, and server block refs.
- `nlm_privileged_requester()` accepts only loopback privileged-port senders for certain local requests.
- `lockd_set_file_lock_range4()` clamps and handles overflow in NLMv4 range conversion.
