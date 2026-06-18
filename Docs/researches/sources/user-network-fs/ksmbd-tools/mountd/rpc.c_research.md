<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc.c

## Purpose

Implements the generic DCE/RPC/NDR engine and named-pipe lifecycle used by ksmbd's RPC IPC support.

## Important APIs, Types, and Functions

Important APIs include pipe table management, `dcerpc_set_ext_payload`, `rpc_pipe_reset`, NDR integer/string/pointer/array helpers, DCE/RPC header read/write, bind parsing/ack/nack, `rpc_open_request`, `rpc_write_request`, `rpc_read_request`, `rpc_ioctl_request`, `rpc_close_request`, and `rpc_restricted_context`.

## Control Flow

Open creates a pipe and DCE context for a kernel handle. Write parses the incoming DCE/RPC header, bind or request header, then dispatches to SRVSVC, WKSSVC, SAMR, or LSARPC write handlers. Read attaches the response buffer, handles bind responses or service read handlers, and writes headers/status. Close removes the pipe. Array helpers estimate how many entries fit in fixed buffers and leave `RETURN_READY` set for continuation.

## State and Persistence Behavior

State includes global `pipes_table` guarded by `GRWLock`, per-pipe pending entries/callbacks, and per-DCE payload cursor, flags, request/response pointers, decoded service-specific request unions, and pointer counters.

## Dependencies and Integration Points

Depends on GLib, endian conversion, kernel RPC ABI, service modules, tools charset conversion, and global anonymous restriction config.

## Risks and Edge Cases

The implementation is deliberately partial and hand-coded; NDR alignment, endian handling, string length, fixed-buffer overflow, multi-fragment responses, and handle cleanup are high-risk. `try_realloc_payload` grows dynamic buffers but fixed external buffers must be exact.

## Test Signals

Tests should cover bind negotiation, unsupported syntaxes/opnums, little/big endian integer round trips, UTF-16 string conversion, fixed-buffer overflow, multi-part share enumeration, pipe collision/close, and restricted-context denial.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc.c -->
