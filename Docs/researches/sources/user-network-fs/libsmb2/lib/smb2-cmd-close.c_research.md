<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c

## Purpose

`smb2-cmd-close.c` encodes and decodes SMB2 CLOSE requests and replies for both client and server roles. It handles file ID transmission and optional close metadata returned by the server.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_close_async`, `smb2_cmd_close_reply_async`, `smb2_process_close_fixed`, and `smb2_process_close_request_fixed`. Internal encoders are `smb2_encode_close_request` and `smb2_encode_close_reply`. Payload structures are `smb2_close_request` and `smb2_close_reply`.

## Control Flow

Request creation allocates an SMB2_CLOSE PDU, appends the fixed request body, sets struct size, flags, and 16-byte file ID, pads to 64-bit alignment, and returns the queued-ready PDU. Reply encoding writes struct size, flags, timestamps, allocation size, EOF, and attributes. Fixed parsers validate exact struct size and body length, allocate payloads, and copy fields from the current input iovec.

## State And Persistence Behavior

The file does not persist state. It creates transient PDU payloads owned by `pdu.c` cleanup. Remote state changes are significant: close releases a server file handle, and close replies can return final metadata.

## Dependencies And Integration Points

It depends on libsmb2 endian helpers and PDU allocation/free/padding. Higher-level file APIs call this when closing `smb2fh` handles.

## Risks And Edge Cases

There is no variable parser because CLOSE has fixed bodies. Encoders that fail after adding an iovec rely on PDU cleanup for allocated buffers. Tests should verify exact size handling because SMB2 struct sizes include the odd wire-size convention masked by `0xfffe`.

## Test Signals

Test round-trip request/reply encoding, flag propagation, file ID copy, metadata fields, malformed struct sizes, short fixed bodies, and close callback behavior through the full async queue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-close.c -->
