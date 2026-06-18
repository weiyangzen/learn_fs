# sources/user-network-fs/samba/source3/libsmb/clioplock.c

## Purpose

This file implements SMB1 oplock-break waiting and acknowledgement. It lets a client register a pending request for the special oplock break MID and send the `LOCKING_ANDX_OPLOCK_RELEASE` acknowledgement when a break is received.

## Important APIs, Types, and Functions

Public APIs are `cli_smb_oplock_break_waiter_send()`, `cli_smb_oplock_break_waiter_recv()`, `cli_oplock_ack_send()`, and `cli_oplock_ack_recv()`. `cli_smb_oplock_break_waiter_state` stores the fnum and new level parsed from the unsolicited break packet; `cli_oplock_ack_state` is only a placeholder for tevent allocation.

## Control Flow

The waiter creates a fake SMB1 request with `smb1cli_req_create()`, sets its MID to `0xffff`, marks it pending with `smbXcli_req_set_pending()`, and waits for the connection layer to complete it with an oplock break packet. The callback validates at least eight words, extracts fnum from word 2 and level from word 3 high byte, and completes. Acknowledgement delegates to `cli_lockingx_send()` with `LOCKING_ANDX_OPLOCK_RELEASE`.

## State and Persistence Behavior

The waiter mutates connection pending-request state by installing the synthetic MID. The ack changes server-side oplock state for an open file. No durable local storage is used.

## Dependencies and Integration Points

The file sits between `smb1cli_req_*`, `smbXcli_req_set_pending()`, and the existing lockingx client code. Callers must be SMB1-aware; SMB2 leases/oplocks are handled elsewhere.

## Risks and Test Signals

Risks include stale fake pending requests, malformed unsolicited packets, incorrect level extraction, and ack failures after a break. Tests should simulate MID `0xffff` completion, short word counts, connection teardown while waiting, valid fnum/level extraction, and server responses to oplock acknowledgements.
