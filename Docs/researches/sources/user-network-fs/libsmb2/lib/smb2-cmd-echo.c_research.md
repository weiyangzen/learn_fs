<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c

## Purpose

`smb2-cmd-echo.c` implements SMB2 ECHO request and reply marshalling. ECHO is a lightweight keepalive/health command with fixed-size empty bodies.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_echo_async`, `smb2_cmd_echo_reply_async`, `smb2_process_echo_fixed`, and `smb2_process_echo_request_fixed`. Internal helpers encode request and reply fixed bodies.

## Control Flow

Client or server allocates an SMB2_ECHO PDU, appends a fixed body containing only the SMB2 struct size, pads to 64-bit alignment, and queues it through `pdu.c`. Fixed parsers validate struct size and length. Request parsing allocates an empty `smb2_echo_request` payload for server handlers.

## State And Persistence Behavior

No durable state exists. ECHO may refresh connection liveness at higher layers but this file does not update counters or timestamps.

## Dependencies And Integration Points

It depends on the core PDU allocator, iovec helper, and endian setters/getters. It is dispatched by `pdu.c` for command `SMB2_ECHO`.

## Risks And Edge Cases

Because the command carries no variable data, most risk is strict size validation and memory allocation for an otherwise empty request. A malformed peer can trigger errors by sending odd or short fixed bodies.

## Test Signals

Test request and reply encoding bytes, parser acceptance of valid bodies, rejection of wrong struct sizes, callback behavior, and use as a keepalive over an established connection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-echo.c -->
