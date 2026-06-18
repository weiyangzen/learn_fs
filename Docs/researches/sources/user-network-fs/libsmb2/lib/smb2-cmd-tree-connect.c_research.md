# sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-connect.c

## Purpose
Implements SMB2 TREE_CONNECT request/reply encoding and parsing, including local tree-id registration and encryption enablement from share flags.

## Important APIs, Types, And Functions
Exports `smb2_cmd_tree_connect_async`, `smb2_cmd_tree_connect_reply_async`, `smb2_process_tree_connect_fixed`, `smb2_process_tree_connect_request_fixed`, and `smb2_process_tree_connect_request_variable`. It consumes `struct smb2_tree_connect_request` and `struct smb2_tree_connect_reply`.

## Control Flow
Request encoding writes flags, path offset, and path length, then appends the caller-provided UTF-16 path bytes. Reply encoding writes share type, share flags, capabilities, and maximal access. Server reply creation can invent a tree id from a static counter when the caller passes zero, connects that tree id in the context, and stamps it into the reply header. Client reply parsing registers the tree id from the SMB2 header, reads share properties, and enables sealing when the share has `SMB2_SHAREFLAG_ENCRYPT_DATA` and sealing was not already set.

## State And Persistence
Tree connection state is persisted in the SMB2 context via `smb2_connect_tree_id`. A static `s_tree_id` is used for server-side synthetic tree ids, so it is process-global rather than context-local. The parsed request path points into the receive iovec.

## Dependencies And Integration Points
This file integrates session-authenticated transport with share-scoped operations. It feeds tree id state used by subsequent create/read/write/query commands and ties share encryption policy into SMB3 sealing.

## Risks
Request parsing returns `path_length` but does not validate `path_offset` for overlap or bounds in this file. The static tree-id counter is not synchronized and can collide across contexts or long-running tests. Path bytes are not converted here; callers must understand UTF-16 path data.

## Test Signals
Cover explicit and auto-generated tree ids, share encryption flag behavior, malformed path offsets/lengths, multiple contexts in server mode, disconnect/reconnect cycles, and paths containing UTF-16 UNC names.
