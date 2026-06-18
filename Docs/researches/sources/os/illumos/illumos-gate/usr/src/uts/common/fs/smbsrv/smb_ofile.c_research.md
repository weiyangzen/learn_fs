# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_ofile.c

## Summary
Implements SMB open-file handles (`smb_ofile_t`): allocation, open completion, close, lookup, sharing checks, durable/persistent handle state, notification cleanup, delete-on-close transfer, per-tree/per-node list membership, NetFile enumeration, and quota resume state.

## Main Responsibilities
- Allocates proposed ofiles before open completion.
- Inserts open handles into tree AVL lists and node ofile lists.
- Maintains the full open/save-durable/orphan/reconnect/expired/closing/closed state machine.
- Looks up handles by SMB FID, unique id, or persistent id.
- Saves durable handles as orphaned handles for reclaim.
- Generates durable and persistent IDs and maintains the server persistent-id hash.
- Closes disk, printer, and pipe handles and releases associated resources.
- Enforces granted-access and share-mode checks.
- Supports delete-on-close, file seek, flush, service enumeration, and quota resume storage.

## Key APIs
- `smb_ofile_alloc()`, `smb_ofile_open()`, `smb_ofile_close()`, `smb_ofile_free()`.
- `smb_ofile_close_all()`, `smb_ofile_drop()`.
- `smb_ofile_hold()`, `smb_ofile_hold_olbrk()`, `smb_ofile_release()`.
- `smb_ofile_lookup_by_fid()`, `smb_ofile_lookup_by_uniqid()`, `smb_ofile_lookup_by_persistid()`.
- `smb_ofile_set_persistid_dh()`, `smb_ofile_set_persistid_ph()`, `smb_ofile_insert_persistid()`, `smb_ofile_del_persistid()`.
- `smb_ofile_open_check()`, `smb_ofile_rename_check()`, `smb_ofile_delete_check()`.
- `smb_ofile_set_delete_on_close()`.

## Important Behavior
`sm b_ofile_alloc()` fills stable open metadata and references user/tree credentials but does not link the object. `smb_ofile_open()` transitions to OPEN, attaches disk/printer handles to the node, inserts into the tree AVL, and increments counters.

`sm b_ofile_close()` first breaks/cleans oplocks for disk files, transitions to CLOSING, closes pipes or disk resources, handles persistent close cleanup, applies delete-on-close, releases share locks and byte-range locks, closes directory searches, cancels notify watchers, commits pending attributes, sends final modified notifications, and decrements counters.

Durable handle preservation uses SAVE_DH and SAVING transient states, removes the handle from tree/user/session ownership, frees the FID, keeps node/lease/notify/open-state data, and exposes the handle as ORPHANED for reconnect by persistent id.

Share checks are symmetric: requested share access is checked against existing granted access, and requested desired access is checked against existing share access. Rename and delete checks implement narrower protocol-specific sharing rules.

## State and Synchronization
The tree ofile AVL lock must be taken before `f_mutex` when both are needed. Persistent-id hash operations must not run while holding `f_mutex`. Oplock-break lookup can hold ofiles in states that normal FID lookup cannot, and waits through RECONNECT/SAVING transitions.

## Dependencies
Depends on SMB2 durable/persistent handle code, oplocks and leases, node open lists, tree/user/session references, ID pools, persistent-id hash tables, pipe support, share-lock and byte-range-lock helpers, file system close/commit, notify state, and NetFile encoding.

## Risks
Durable handle state is deliberately kept on the node ofile list after tree/user/session references are removed. Callers must respect state-specific field validity, especially during ORPHANED and RECONNECT.

`sm b_ofile_flush()` notes that named-pipe flush should drain writes but currently does nothing for pipe types.

Close and durable-save paths use deferred list posts to avoid deleting while iterating; refcount leaks can keep handles in SAVE_DH until durable timers force closure.
