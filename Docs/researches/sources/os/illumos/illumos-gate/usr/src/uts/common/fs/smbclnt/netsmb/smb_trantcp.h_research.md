# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.h

## Scope

This header defines NetBIOS-over-TCP transport state and connection control block fields.

## APIs And Definitions

- `enum nbstate` models closed, idle, request-sent, session, retarget, and refused states.
- `struct nbpcb` stores the SMB virtual circuit pointer, KTLI handle, receive fragment, local/peer NetBIOS addresses, select ID, held credential, flags, file mode, state, timeout, buffer sizes, mutex, and condition variable.
- Flag bits include local address present, connected, receive lock, send lock, and lock wait.
- Defines nominal send/receive queue sizes, receive chunk size, and socket buffer timeout constants.

## Dependencies

- Used directly by `smb_trantcp.c`.
- Depends on `struct smb_vc`, `struct tiuser`, STREAMS `mblk_t`, sockaddr NetBIOS, credentials, mutexes, and condition variables.

## Risks And Invariants

- `nbp_frag` ownership belongs to the receive path and must be freed with endpoint teardown.
- `NBF_RECVLOCK` and `NBF_SENDLOCK` are required to prevent concurrent directional transport access.
