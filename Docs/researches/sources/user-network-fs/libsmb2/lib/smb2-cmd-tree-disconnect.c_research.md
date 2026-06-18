# sources/user-network-fs/libsmb2/lib/smb2-cmd-tree-disconnect.c

## Purpose
Implements the small SMB2 TREE_DISCONNECT request/reply and removes tree-id state when a disconnect reply is processed.

## Important APIs, Types, And Functions
Exports `smb2_cmd_tree_disconnect_async`, `smb2_cmd_tree_disconnect_reply_async`, `smb2_process_tree_disconnect_fixed`, and `smb2_process_tree_disconnect_request_fixed`.

## Control Flow
Request and reply encoding each allocate a four-byte fixed payload and write the structure size. The async wrappers allocate a `SMB2_TREE_DISCONNECT` PDU and pad it. Client reply processing calls `smb2_disconnect_tree_id` with the tree id from the SMB2 header. Server request parsing is a no-op because the command has no variable body.

## State And Persistence
The only state mutation is removal of the current header tree id from the SMB2 context. No payload data is retained.

## Dependencies And Integration Points
This command closes the lifecycle started by TREE_CONNECT and affects all later tree-scoped operations. It uses generic PDU allocation, iovectors, padding, and tree-id registry helpers.

## Risks
The fixed request parser does not check the incoming structure size in this file, so malformed disconnect requests rely on generic sizing elsewhere. Disconnecting based solely on header tree id is correct for SMB2 but needs tests around stale or unknown ids.

## Test Signals
Test normal connect/disconnect, disconnect of missing tree ids, malformed fixed payloads, server-mode disconnect requests, and ensuring later tree-scoped commands fail or select a different tree.
