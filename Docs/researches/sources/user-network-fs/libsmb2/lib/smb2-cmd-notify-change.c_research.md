<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c

## Purpose

`smb2-cmd-notify-change.c` implements SMB2 CHANGE_NOTIFY request and reply marshalling. It allows clients to ask for directory change notifications and lets servers return raw notification buffers.

## Important APIs, Types, And Functions

Public functions are `smb2_cmd_change_notify_async`, `smb2_cmd_change_notify_reply_async`, `smb2_process_change_notify_fixed`, `smb2_process_change_notify_variable`, and `smb2_process_change_notify_request_fixed`. Payloads are `smb2_change_notify_request` and `smb2_change_notify_reply`.

## Control Flow

Request encoding writes flags, output buffer length, file ID, and completion filter. Reply encoding writes output buffer offset/length and, only in passthrough mode, appends caller-provided raw output. Fixed reply parsing validates the fixed body, reads output metadata, and returns the output length. Variable parsing points the output at the variable iovec. Request parsing reads flags, file ID, and completion filter.

## State And Persistence Behavior

No local state persists. On the server, CHANGE_NOTIFY can create a pending asynchronous operation until a directory changes; async correlation is handled by `pdu.c` and higher server logic.

## Dependencies And Integration Points

It depends on libsmb2 PDU helpers and passthrough mode. Notification output structure packing is not implemented except for raw passthrough, so proxy/server users must supply wire-format data.

## Risks And Edge Cases

Reply encoding sets `output_buffer_offset` using `SMB2_CHANGE_NOTIFY_REQUEST_SIZE` instead of the reply fixed size, which should be checked against protocol constants. Structured notification packing is not implemented. Fixed parsing returns `output_buffer_length` without validating the received output offset. Variable output pointer lifetime is tied to the PDU receive buffer.

## Test Signals

Test request filter/flag encoding, output offset/length correctness, zero-output replies, passthrough raw notification buffers, async pending/complete flow, malformed output lengths, and integration with directory watch operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-notify-change.c -->
