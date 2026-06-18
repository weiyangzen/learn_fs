# sources/user-network-fs/samba/source3/include/async_smb.h

## Purpose
`async_smb.h` declares tevent-based helpers for constructing, sending, and receiving asynchronous SMB1 client requests.

## Important APIs, Types, And Functions
- `cli_smb_req_create()` creates a `tevent_req` from SMB command metadata, word parameters, and byte iovecs.
- `cli_smb_send()` sends a request using a contiguous byte buffer.
- `cli_smb_recv()` receives and validates a response, returning the input buffer, word count/vector, byte count, and bytes.

## Control Flow
Callers create or send a request on a `cli_state` with a `tevent_context`, then later call `cli_smb_recv()` when the tevent request completes. The receive API enforces a minimum word count.

## State And Persistence
No persistent state is defined. Requests are talloc/tevent-owned and operate over the live SMB client connection.

## Dependencies And Integration Points
It depends on `struct cli_state`, `tevent_req`, `tevent_context`, `iovec`, `TALLOC_CTX`, and `NTSTATUS`. It integrates low-level SMB client code with Samba's async event model.

## Risks
Callers must keep parameter and byte buffers valid according to request ownership rules. Incorrect `min_wct` or iovec lengths can cause protocol parsing failures. These APIs are SMB1-oriented and should be guarded from SMB2-only assumptions.

## Test Signals
Async tests should cover simple request/response, malformed short responses, multi-iovec byte payloads, timeout/cancel behavior, and memory ownership after receive.
