# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_node.c

## Summary
Implements the SMB server's `smb_node_t` layer: a cached vnode wrapper with SMB-specific state for parent/stream relationships, open-handle lists, share checks, delete-on-close, change notify fanout, sticky timestamps, simulated allocation size, reparse/DFS flags, and system-file marking.

## Main Responsibilities
- Initializes and destroys the global SMB node kmem cache and hash table.
- Looks up or allocates nodes from vnode identity, share fsid, and file attributes.
- Maintains node references and the AVAILABLE/DESTROYING state machine.
- Tracks parent directory nodes and unnamed-stream backing nodes.
- Applies open/share/delete/rename conflict checks across open files.
- Manages delete-on-close credentials and final removal.
- Provides change notification subscription and event dispatch to open handles.
- Exposes node path, mount path, file type, reparse, system, and readonly helpers.
- Applies SMB timestamp and allocation-size semantics around filesystem setattr/getattr.

## Key APIs
- `smb_node_init()`, `smb_node_fini()`.
- `smb_node_lookup()`, `smb_stream_node_lookup()`.
- `smb_node_ref()`, `smb_node_release()`.
- `smb_node_set_delete_on_close()`, `smb_node_reset_delete_on_close()`, `smb_node_delete_on_close()`.
- `smb_node_open_check()`, `smb_node_rename_check()`, `smb_node_delete_check()`.
- `smb_node_fcn_subscribe()`, `smb_node_fcn_unsubscribe()`, `smb_node_notify_change()`, `smb_node_notify_modified()`.
- `smb_node_setattr()`, `smb_node_getattr()`.

## Important Behavior
`sm b_node_lookup()` uses `smb_vop_getattr()` with zone credentials, chooses the tree fsid for share-relative objects, searches a hash bucket by hash key and vnode pointer, and ignores nodes already in DESTROYING state. A new node takes its own vnode hold and optional holds on parent and unnamed-stream nodes.

Reference teardown moves a zero-ref node to DESTROYING before dropping `n_mutex`, preventing concurrent lookup from resurrecting a node while `smb_node_release()` removes it from the hash table.

Delete-on-close is stored on the node with the credential and case flags that will be used for final `smb_fsop_remove()` or `smb_fsop_rmdir()`. Directories are checked for emptiness before accepting delete-on-close. A delete-pending notify event is sent so change-notify waiters stop using the handle.

The file simulates Windows semantics not directly represented by illumos VFS. Allocation size persists only while opens exist. Special NT time values `-1` and `-2` pause or resume per-handle sticky timestamps; sticky values are returned through handle-based getattr and committed on close.

## State and Synchronization
Node lifetime is governed by the hash-bucket list lock plus `n_mutex`; the documented lock order is bucket lock before node mutex. `n_ofile_list` is protected separately and is used by share checks, notifications, and oplock/open-handle walkers. Share-reservation critical regions combine `n_lock` with `nbl_start_crit()`/`nbl_end_crit()`.

## Dependencies
Depends on SMB fsop/vop wrappers, FEM hooks, oplock state, named streams/xattr directories, reparse parsing, DFS reparse type detection, change notify, DOS attributes, and illumos vnode/pathname APIs.

## Risks
The node hash uses fsid and nodeid but final identity includes vnode pointer, so correctness depends on stable vnode identity for the lifetime of cached nodes.

`sm b_node_rename()` updates parent and on-disk name but explicitly notes that attributes may need updating.

The delete-on-close path can run filesystem remove/rmdir during final close/release, so failures are logged but cannot be surfaced cleanly to the original client operation.

Directory emptiness checking reads a single readdir buffer and treats malformed or partial records conservatively as non-empty.
