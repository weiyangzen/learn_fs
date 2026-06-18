<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c

## Purpose

`smb2-cmd-error.c` handles SMB2 ERROR response bodies. It is used when `pdu.c` classifies the SMB2 status as an error or selected warning and needs command-independent error payload parsing.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_error_reply_async`, `smb2_process_error_fixed`, and `smb2_process_error_variable`. Internal `smb2_encode_error_reply` writes the fixed error body. The payload type is `smb2_error_reply`.

## Control Flow

Error reply creation allocates a PDU using the causing command, sets `header.status`, encodes struct size, error context count, and byte count, then pads. Fixed parsing validates the error body, allocates payload, reads context count and byte count, and returns the variable byte count. Variable parsing points `error_data` at the variable iovec.

## State And Persistence Behavior

No persistent state is used. Error data pointers reference receive-buffer lifetime owned by the PDU. The header status is the main error state and is set before queueing.

## Dependencies And Integration Points

The module is integrated with `smb2_is_error_response` in `pdu.c`; command-specific parsers are bypassed for error statuses. Server code can create errors for any causing command.

## Risks And Edge Cases

Encoding has a TODO for structured error data, so server-side rich error contexts are not emitted. Variable parsing does not decode context records and exposes raw bytes. Consumers must not use `error_data` after the PDU is freed.

## Test Signals

Test status propagation, byte count variable reads, raw error-data lifetime, malformed fixed sizes, zero-byte errors, and errors attached to each command type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-error.c -->
