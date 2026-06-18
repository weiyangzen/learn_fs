<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c

## Purpose

`smb2-cmd-logoff.c` implements SMB2 LOGOFF request and reply marshalling. LOGOFF terminates an SMB2 session after tree and file cleanup at higher protocol layers.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_logoff_async`, `smb2_cmd_logoff_reply_async`, `smb2_process_logoff_fixed`, and `smb2_process_logoff_request_fixed`. Internal helpers encode fixed request and reply bodies.

## Control Flow

Request and reply encoding allocate a small fixed body, write the struct size, pad, and return a PDU. Client-side reply fixed processing is a no-op. Server-side request parsing validates the fixed body, allocates an empty `smb2_logoff_request`, and stores it as payload.

## State And Persistence Behavior

The file itself holds no state. Remote/session state changes happen when a server processes LOGOFF; context session cleanup is handled elsewhere.

## Dependencies And Integration Points

It plugs into `pdu.c` dispatch for `SMB2_LOGOFF`. LOGOFF PDUs use tree ID zero in `smb2_allocate_pdu`.

## Risks And Edge Cases

`smb2_process_logoff_request_fixed` compares against `SMB2_ECHO_REQUEST_SIZE` and reports echo sizes/messages rather than `SMB2_LOGOFF_REQUEST_SIZE`; this is probably harmless only if those constants are identical. The allocation error also says echo request. Tests should guard against future constant divergence.

## Test Signals

Test request/reply byte encoding, parser size constants, session-id preservation in headers, tree-id zero handling, and full disconnect/logoff sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-logoff.c -->
