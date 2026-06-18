# sources/user-network-fs/samba/source3/libsmb/async_smb.c

## Purpose
`async_smb.c` provides async SMB1 client request helpers wrapping `smb1cli_req_*` for source3 `cli_state` users. It creates requests, tracks command-specific receive behavior, maps legacy DOS errors if configured, and returns parsed SMB1 response components.

## Important APIs, types, and functions
- `struct cli_smb_req_state` stores the `cli_state`, SMB command, underlying request, and a pointer sentinel used for lifetime coordination.
- `cli_smb_req_create()` creates a request from word count/vector words and byte iovecs.
- `cli_smb_send()` creates and sends a request from a flat byte buffer.
- `cli_smb_recv()` receives/parses the response, validates minimum word count, maps errors, and returns optional input buffer, words, and bytes.
- Two destructors coordinate state/request ownership when either the state or pointer sentinel is freed.

## Control flow
Create/send allocates state, allocates `state->ptr`, builds the underlying `smb1cli` request using connection/session/tree IDs from `cli_state`, reparents the sentinel under the request, and installs destructors. Receive calls `smb1cli_req_recv()`, then applies command-specific exceptions: `SMBsesssetupX` may legitimately return `NT_STATUS_MORE_PROCESSING_REQUIRED`, and `SMBntcreateX` with `NT_STATUS_STOPPED_ON_SYMLINK` lowers the minimum word count to zero. DOS errors are optionally converted to NTSTATUS. Successful or expected responses return parsed buffers.

## State and persistence behavior
State is entirely in-memory and talloc-owned. The destructor pattern ensures the wrapper state follows the request lifetime and can still recover command/client context during receive. No durable state is changed.

## Dependencies and integration points
It depends on `cli_state`, tevent, `smbXcli_base`, and client headers. Higher-level SMB1 client operations use these helpers to integrate old `cli_state` code with asynchronous request infrastructure.

## Risks and edge cases
The paired destructor/reparenting logic is subtle and can cause use-after-free or leaks if changed. `cli_smb_recv()` treats all non-error status as expected, but only explicitly allows some error statuses. Mapping DOS errors preserves legacy behavior but may hide raw wire status. Response buffer ownership depends on talloc reference counts and optional `pinbuf`.

## Test signals
Test request lifetime when callers cancel/free requests early, SMB session setup continuation, symlink stopped responses, DOS error mapping enabled/disabled, minimum word-count validation, iovec and flat-byte sends, and memory ownership with/without `pinbuf`.
