# sources/user-network-fs/libsmb2/lib/smb2-cmd-write.c

## Purpose
Builds SMB2 WRITE requests/replies and parses WRITE replies/requests for client and server paths.

## Important APIs, Types, And Functions
Key functions are `smb2_cmd_write_async`, `smb2_cmd_write_reply_async`, `smb2_process_write_fixed`, `smb2_process_write_request_fixed`, and `smb2_process_write_request_variable`. It uses `struct smb2_write_request` and `struct smb2_write_reply`.

## Control Flow
Request encoding emits data offset, length, offset, file id, channel, remaining bytes, optional write channel info, and flags. It caps writes above 64 KiB when multi-credit is unavailable. `smb2_cmd_write_async` pads the header vectors, then appends the caller's data buffer with optional ownership transfer, and sets multi-credit charge for large writes. Reply encoding writes count and remaining bytes. Request parsing extracts fixed fields, validates channel-info overlap when present, and returns enough variable length to include channel info padding plus data. Variable parsing exposes channel info and write data as zero-copy pointers into the receive iovec.

## State And Persistence
Write data can be owned by the PDU when `pass_buf_ownership` is true. Parsed inbound request buffers point into the PDU input vector and should not outlive PDU cleanup. Credit consumption is persisted through the PDU header.

## Dependencies And Integration Points
This file depends on iovec-based zero-copy sends/receives, credit charging, PDU padding, and server callbacks for writes. It pairs with `socket.c` logic that writes compound vectors and reads variable request data.

## Risks
The passthrough channel-info offset assignment uses `SMB2_READ_REQUEST_SIZE` instead of the write request size, which is likely a bug. Request parsing does not validate data offset directly; it derives the data pointer after padded channel info. Unsupported structured channel info returns an error unless passthrough is enabled.

## Test Signals
Exercise small and large writes with and without multi-credit, ownership and non-ownership buffers, malformed data/channel offsets, zero-length writes, passthrough channel info, and server-side zero-copy lifetime.
