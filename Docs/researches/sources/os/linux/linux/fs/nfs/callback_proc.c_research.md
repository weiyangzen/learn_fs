# File Research: sources/os/linux/linux/fs/nfs/callback_proc.c

## Purpose
Implements the semantic handlers for decoded NFSv4 callback operations. It updates delegation, layout, device-id, slot/session, lock, and NFSv4.2 offload-copy state after `callback_xdr.c` decodes the wire data.

## Main Responsibilities
- Answer `CB_GETATTR` from delegated inode state.
- Process delegation recalls through asynchronous delegation return.
- Process layout recalls for files, FSIDs, or all layouts.
- Process pNFS device notifications by deleting cached device IDs.
- Validate and advance NFSv4.1+ backchannel sequence slots.
- Process recall-any and recall-slot pressure signals.
- Wake waiters for server lock notifications.
- Record NFSv4.2 server-side-copy offload completion callbacks.

## Key Functions
- `nfs4_callback_getattr()` finds a delegated inode and returns requested size/change/time attributes for write delegations.
- `nfs4_callback_recall()` finds a delegated inode and schedules delegation return.
- `nfs4_callback_layoutrecall()` dispatches to file or bulk pNFS layout draining.
- `nfs4_callback_devicenotify()` deletes matching pNFS device IDs using the relevant layout driver.
- `nfs4_callback_sequence()` resolves the callback session, validates slot/sequence/cache rules, handles referring calls, and locks the backchannel slot.
- `nfs4_callback_recallany()` expires matching unused delegations and triggers layout recalls or flexfile recall-any state.
- `nfs4_callback_recallslot()` lowers target forechannel slot limits and notifies the state manager.
- `nfs4_callback_notify_lock()` wakes lock waiters when decoded owner data is valid.
- `nfs4_callback_offload()` records asynchronous copy completion by matching or queueing a copy state.

## Layout Recall Flow
File layout recall first locates an inode by layout stateid, falling back to filehandle. It commits layout data, validates callback stateid sequencing, checks for bulk recall conflicts, updates the layout stateid, marks matching layout segments for return, frees matching lsegs, and kicks commit cleanup. Bulk recall destroys layouts by FSID or client ID.

## Sequence Handling
`nfs4_callback_sequence()`:
- Finds the client/session from session ID and source address.
- Rejects missing sessions or sessions without backchannel.
- Rejects draining sessions with `DELAY` or `BADSESSION`.
- Validates slot ID and sequence ID.
- Rejects cached-reply requests because the client does not implement a duplicate reply cache.
- Waits briefly on referring forechannel calls before allowing dependent callbacks.
- Stores the slot in `cb_process_state` for later release by XDR compound cleanup.

## Data and Ownership
- `CB_SEQUENCE` frees referring-call allocations after processing.
- `CB_DEVICE_NOTIFY` frees decoded device notification arrays.
- Inode references acquired through delegation/layout lookup are released with `nfs_iput_and_deactive()`.
- Layout headers are refcounted with `pnfs_get_layout_hdr()`/`pnfs_put_layout_hdr()`.

## Status Mapping
Handlers return NFS protocol status values in big-endian form. Common mappings include:
- Missing session/client: `NFS4ERR_OP_NOT_IN_SESSION` or `NFS4ERR_BADSESSION`.
- Missing delegation inode: `NFS4ERR_BADHANDLE`, `NFS4ERR_DELAY`, or `NFS4ERR_BAD_STATEID`.
- Layout stateid mismatch: `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_DELAY`, or `NFS4ERR_NOMATCHING_LAYOUT`.
- Successful callbacks return `NFS4_OK`.

## Risks and Edge Cases
- `referring_call_exists()` drops and reacquires the slot-table lock while waiting, so callers must tolerate state changes.
- Layout recall sequencing depends on referring-call count to decide whether a future stateid should be trusted.
- `CB_GETATTR` only supplies attributes when a valid write delegation exists.
- Offload callback stores unmatched completions in `pending_cb_stateids`; cleanup is handled elsewhere.

## Integration Points
This file ties callbacks to delegation management (`delegation.c`), pNFS layout management, NFSv4 session slot code, lock wait queues, copy offload state, and NFS tracepoints.
