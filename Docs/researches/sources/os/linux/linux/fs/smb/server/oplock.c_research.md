# File Research: sources/os/linux/linux/fs/smb/server/oplock.c

This file implements ksmbd SMB2/SMB3 oplocks, leases, break notifications, create-context helpers, and durable-handle reconnect validation.

Core data organization:
- Per-inode oplock records live on `ksmbd_inode::m_op_list`, protected by the inode `m_lock`.
- Lease records are additionally indexed in global `lease_table_list`, keyed by SMB2 client GUID and protected by `lease_list_lock`.
- `oplock_info` lifetime is refcounted and freed via RCU. File pointers publish `f_opinfo` with RCU assignment.
- Separate per-inode counters distinguish normal file oplocks and stream oplocks.

Allocation/lifetime:
- `alloc_opinfo()` initializes wait queues, refcounts, connection reference, FID, TID, state, and level.
- `alloc_lease()` creates lease state from parsed create context.
- `close_id_del_oplock()` removes list entries, clears `fp->f_opinfo`, wakes waiters if a break is pending, decrements counts, and releases refs.
- `destroy_lease_table()` removes all lease-table entries for a connection or globally.

State transitions:
- `opinfo_write_to_read`, `opinfo_read_handle_to_read`, `opinfo_write_to_none`, and `opinfo_read_to_none` apply acknowledged break transitions.
- `lease_read_to_write()` and `lease_none_upgrade()` handle same-client lease upgrades.
- `smb2_map_lease_to_oplock()` maps R/H/W lease-state combinations to batch, exclusive, level II, or none.

Break handling:
- `oplock_break_pending()` serializes concurrent break operations using a bit wait.
- `oplock_break()` computes target state, sends interim responses when needed, marks `OPLOCK_ACK_WAIT`, sends oplock or lease break notifications, waits for acknowledgements/timeouts, and wakes waiters.
- `smb2_oplock_break_noti()` and `smb2_lease_break_noti()` build async SMB2 break notifications.
- `smb_break_all_write_oplock`, `smb_break_all_levII_oplock`, and `smb_break_all_oplock` are called by write/truncate and open paths to invalidate client caching.

Grant path:
- `smb_grant_oplock()` handles file-create requested oplock/lease levels, directory lease constraints, same-client lease reuse/upgrade, share-mode conflicts, breaking previous exclusive/batch owners, stacked lease/oplock restrictions, and final publication.
- It preallocates a new lease table before publishing `opinfo` to inode/global lists, avoiding failure after concurrent readers can see the object.

Create-context helpers:
- `parse_lease_state()` extracts v1/v2 lease create contexts.
- `smb2_find_context_vals()` walks create contexts with alignment, length, and bounds validation.
- Response builders create lease, durable handle v1/v2, maximal access, disk ID, and POSIX extension contexts.

Durable reconnect:
- `lookup_lease_in_table()` finds a breakable lease for client GUID and lease key.
- `smb2_check_durable_oplock()` validates durable reconnect owner, client GUID, lease key, handle-caching state, lease version, batch oplock requirements, and path/name validity unless pending delete.

Concurrency notes:
- Uses RCU for `f_opinfo` and lease-list iteration, refcounts before dropping RCU read locks, wait queues for break acknowledgements, and atomic counters for concurrent break state.
- Calls avoid operating on connections in releasing state.
- Timeout paths downgrade caching to none when clients do not acknowledge.

Role in this group:
- Declared by `oplock.h`.
- Called from SMB2 create, write, truncate, close, lease-break acknowledgement, durable reconnect, and VFS mutation paths.
