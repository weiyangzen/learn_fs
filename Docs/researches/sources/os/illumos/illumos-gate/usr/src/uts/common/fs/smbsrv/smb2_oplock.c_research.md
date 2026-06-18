# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_oplock.c

Implements SMB2 oplock break acknowledgements, oplock break notifications, oplock acquisition, send-break fallback behavior, and durable-handle reconnect state restoration.

Key behavior:
- `smb2_oplock_break_ack()` decodes either oplock break ACK or forwards lease ACKs to `smb2_lease_break_ack()`.
- Converts SMB2 oplock levels to internal `OPLOCK_LEVEL_*` values and validates unsolicited ACKs.
- Updates open-file oplock state under node oplock locks and broadcasts ACK condition variables.
- `smb2_oplock_send_break()` sends asynchronous oplock break notifications, waits for ACKs when required, closes non-durable opens if disconnected, or performs a local ACK fallback.
- `smb2_oplock_acquire()` grants batch/exclusive/shared oplocks when eligible, honors tree settings forcing level-II oplocks, updates durable handle state, and waits asynchronously for break-in-progress cases.
- `smb2_oplock_reconnect()` reconstructs SMB2 oplock or lease state for durable-handle reconnect responses.

Important dependencies:
- Common oplock engine: `smb_oplock_request`, `smb_oplock_ack_break`, `smb_oplock_wait_ack`, `smb_oplock_wait_break`.
- Open/node locking: `node->n_ofile_list`, `node->n_oplock.ol_mutex`.
- Durable handles: `smb2_dh_update_oplock`.
- Transport: `smb_session_send`.

Notable details:
- Lease break handling is deliberately delegated to `smb2_lease.c`.
- If a client cannot receive a required break ACK, the server must locally ACK to clear filesystem-level breaking state.
