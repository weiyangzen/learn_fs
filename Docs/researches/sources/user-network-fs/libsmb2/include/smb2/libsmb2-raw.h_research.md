# sources/user-network-fs/libsmb2/include/smb2/libsmb2-raw.h

## Purpose
`libsmb2-raw.h` exposes the low-level asynchronous SMB2 command interface. It lets applications build raw SMB2 PDUs directly and also provides reply helpers for server/proxy use.

## Important APIs, Types, and Functions
The header declares `compound_file_id`, `smb2_free_data()`, and one or more async functions for negotiate, session setup, tree connect/disconnect, create, close, read, write, query directory, change notify, query info, set info, ioctl, echo, lock, logoff, flush, oplock/lease break, and error replies. Many commands have both request and reply creation helpers, such as `smb2_cmd_create_async()` and `smb2_cmd_create_reply_async()`.

## Control Flow
Callers allocate command PDUs with raw async functions, optionally compound them through the public PDU helpers, queue them, and drive socket progress with `smb2_service()`. Completion arrives through `smb2_command_cb`, with command-specific decoded payloads or NT status errors.

## State and Persistence Behavior
Raw calls create `struct smb2_pdu` objects and decoded output buffers. PDU lifetime is explicit: callers must free PDUs as documented, and query/ioctl output buffers are freed through `smb2_free_data()`. No disk persistence.

## Dependencies and Integration Points
It depends on protocol structs from `smb2.h` and callbacks/context from `libsmb2.h`. High-level POSIX-like APIs in `libsmb2.c` build on this layer, while server/proxy code uses reply helpers.

## Risks and Edge Cases
The raw layer exposes wire-level sizes, ownership, and callback semantics; callers can create invalid request combinations. Some comments are copy-pasted with inaccurate command names, so behavior should be verified against signatures and implementation.

## Test Signals
Build raw compound stat/open/read/write flows, cancel PDUs before callbacks, test server reply helpers, validate output-buffer freeing, and fuzz malformed request structs where internal validation should reject them.
