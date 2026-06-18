# File Research: sources/os/linux/linux-stable/fs/nfs/callback_proc.c

## Purpose

`callback_proc.c` implements the semantics of NFSv4 callback operations after XDR decoding. It handles delegation getattr/recall, pNFS layout recall and device notifications, NFSv4.1 session sequencing, recall-any and recall-slot, lock notification, and NFSv4.2 server-side-copy offload completion callbacks.

## Main Responsibilities

- Answer callback `GETATTR` from delegated inode state.
- Process delegation recall by scheduling asynchronous delegation return.
- Locate pNFS layouts by stateid or filehandle and initiate file or bulk layout draining.
- Delete pNFS device IDs on device notify callbacks.
- Validate and advance NFSv4.1 callback sequence slots.
- Detect referring calls that are still pending on the forechannel.
- Expire unused delegations and recall pNFS layouts for `CB_RECALL_ANY`.
- Reduce forechannel slot table target for `CB_RECALL_SLOT`.
- Wake lock waiters for `CB_NOTIFY_LOCK`.
- Complete or record NFSv4.2 copy offload callback state.

## Key Functions

- `nfs4_callback_getattr()` finds a delegated inode, verifies a valid write delegation, and returns change, size, and requested time attributes.
- `nfs4_callback_recall()` finds the delegated inode and calls `nfs_async_inode_return_delegation()`, mapping kernel errors to NFS callback status codes.
- `nfs_layout_find_inode_by_stateid()` and `nfs_layout_find_inode_by_fh()` search all superblocks and layouts for a matching pNFS layout.
- `pnfs_check_callback_stateid()` enforces RFC5661 layout recall sequencing, including old, delayed, and mismatched stateid handling.
- `initiate_file_draining()` commits pending layout data, validates stateid, marks matching layout segments for return, and may call the layout driver's `return_range()`.
- `initiate_bulk_draining()` destroys layouts by FSID or client ID for bulk recall.
- `nfs4_callback_devicenotify()` finds the relevant layout driver and deletes device IDs from the cache.
- `nfs4_callback_sequence()` finds the client/session, validates slot and sequence ID, locks the backchannel slot, checks cachethis constraints, records referring-call status, and updates the slot sequence.
- `nfs4_callback_recallany()` handles delegation and layout recall masks and schedules the state manager for file-layout recall-any flags.
- `nfs4_callback_offload()` matches copy state by stateid, completes a waiting copy, or queues pending callback state if the local copy state is not present yet.

## Control Flow and State

For NFSv4.1+, `CB_SEQUENCE` must run first and populates `cps->clp`, `cps->slot`, and `cps->referring_calls`. Later operations in the same compound depend on that state. The sequence path uses the backchannel slot table lock to reject bad slots, replays, misordered sequence IDs, draining sessions, and unsupported cached replies.

Layout recall uses RCU to find candidate layouts, active-superblock references to prevent unmount races, inode references for stable processing, inode locks for layout header state, and pNFS layout reference helpers for lifetime. Delegation callbacks integrate with delegation lookup and asynchronous state manager return queues.

## Integration Points

- Delegation operations call into `delegation.c` through `nfs_delegation_find_inode()`, `nfs4_get_valid_delegation()`, and `nfs_async_inode_return_delegation()`.
- pNFS operations use layout header state, layout segment return marking, device-id deletion, layout driver lookup, and layoutcommit/commit helpers.
- Session operations use `nfs4session.h` slot-table helpers.
- v4.2 offload integrates with `struct nfs4_copy_state` lists on `nfs_server` and `nfs_client`.
- Tracepoints in `nfs4trace.h` record callback outcomes.

## Risks and Edge Cases

- `nfs_layout_find_inode_by_stateid()` is annotated `__must_hold(RCU)` but also calls `rcu_read_lock()` internally; reviewers should keep lockdep expectations in mind around this helper.
- Layout recall sequencing intentionally returns `NFS4ERR_DELAY` in several race windows, including stateid gaps without referring-call evidence and already-returning layouts.
- `referring_call_exists()` drops and reacquires the slot-table lock while waiting on forechannel sequence IDs.
- Device notify ignores unknown layout drivers and continues; this is tolerant but can leave unsupported layout driver device IDs untouched.
- Offload callback handling must handle callback-before-waiter and waiter-before-callback races.

## Testing Focus

Important coverage includes v4.1 sequence replay/misorder cases, callback compounds missing `CB_SEQUENCE`, layout recall file/stateid mismatch, bulk layout recall, device notify delete/change, recall-any masks, recall-slot target changes, lock owner wakeups, delegation getattr with and without write delegation, and v4.2 offload completion races.
