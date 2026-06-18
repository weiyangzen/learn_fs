<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_oplock.c

## Purpose
`smb1_oplock.c` builds and sends SMB1 oplock break notifications. It is the SMB1-specific wire-format adapter used when Samba needs to tell a client to release or downgrade an oplock on an open file.

## Important APIs, types, and functions
`new_break_message_smb1(files_struct *fsp, int cmd, char result[SMB1_BREAK_MESSAGE_LENGTH])` initializes an SMB1 `SMBlockingX` oplock break message. It zeroes the SMB header, calls `srv_smb1_set_message(result, 8, 0, true)`, sets command, tree id, PID/UID/MID sentinel values, AndX terminator, target FID, `LOCKING_ANDX_OPLOCK_RELEASE`, and the requested break command/level byte.

`send_break_message_smb1(files_struct *fsp, int level)` selects the sole SMB1 connection from `fsp->conn->sconn->client->connections`, builds the break message, logs it with `show_msg()`, and sends it with `smb1_srv_send()` using the connection encryption state. Send failure is fatal and calls `exit_server_cleanly()`.

## Control flow
The generic oplock/lease break path calls the SMB1 send routine for files opened over SMB1. The code assumes SMB1 has exactly one connection for the client, builds a fixed-size break frame on the stack, and sends it synchronously. No reply is expected from these functions; any client response is handled by separate locking/oplock release paths.

## State and persistence behavior
The module does not persist state itself. It reads `files_struct` fields (`fnum`, connection, tree id, encryption status) and writes a transient network message. The resulting client behavior may later alter oplock/share-mode state elsewhere.

## Dependencies and integration points
It depends on SMB1 packet layout helpers, `files_struct`, `connection_struct`, SMB1 send code, lock/oplock constants, and server-exit behavior. The included lease/share-mode headers reflect its placement in the broader locking subsystem, though this file only formats and sends the SMB1 break message.

## Risks and edge cases
The wire layout is small but exact: incorrect word count, FID, command byte, or sentinel IDs can make clients ignore oplock breaks. The single-connection assumption is explicit for SMB1; using this helper for SMB2/multichannel would be wrong. Send failure terminates the server process cleanly because failing to deliver an oplock break can compromise cache coherency.

## Test signals
Tests should verify the exact SMB1 bytes produced by `new_break_message_smb1()` for representative FIDs/tree ids and break levels, including `SMBlockingX`, `LOCKING_ANDX_OPLOCK_RELEASE`, `0xFFFF` PID/MID, and word count. Integration tests should open an SMB1 file with an oplock, trigger a conflicting open, confirm the break message is sent encrypted when the tree is encrypted, and verify server behavior on simulated send failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.c -->
