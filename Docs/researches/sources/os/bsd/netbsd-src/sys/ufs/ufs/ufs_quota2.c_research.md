# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota2.c

This file implements UFS quota v2. Quota entries live in quota files with a header, default entry, hash lists, and free lists. The implementation supports journaled allocation/update of quota entries and cursor-based iteration.

Key responsibilities:
- Enforce block and file quota2 limits with shared limit-checking logic.
- Locate, allocate, delete, and update quota2 entries in on-disk hash/free-list structures.
- Convert quota2 on-disk values to and from fs-independent `quotaval`.
- Implement `quotactl` get/put/delete and cursor iteration for quota2.
- Track quota2 entry locations in `struct dquot`.
- Provide mount unmount cleanup for quota2 files.

Important functions:
- `getq2h`: Reads and validates the quota2 header block.
- `getq2e`: Reads a quota2 entry by logical block and block offset.
- `quota2_walk_list`: Walks a quota2 linked list, optionally allowing callbacks to modify parent pointers.
- `quota2_q2ealloc`: Allocates a free quota entry, extending the quota file if needed, initializes it from the default entry, and inserts it into the hash list.
- `getinoquota2`: Gets all relevant dquots for an inode, locks them, optionally allocates missing on-disk entries, and returns buffers/entry pointers.
- `quota2_check`: Shared block/file accounting path used by `chkdq2` and `chkiq2`; handles negative deltas, limit checks, warnings, soft-limit crossing times, and usage updates.
- `quota2_handle_cmd_put`: Updates default limits or a specific ID’s quota entry inside a WAPBL transaction.
- `quota2_handle_cmd_del`: Resets one object type to defaults and frees the entry if it no longer carries usage or custom limits.
- `quota2_handle_cmd_get`: Reads default or ID-specific quota values.
- Cursor helpers: Validate cursor state, scan hash buckets, return block/file key-value pairs, skip ID types, test end state, and rewind.
- `dq2get`: Locates an existing quota2 entry and stores its disk location in the dquot.
- `q2sync` / `dq2sync`: No-op because quota2 writes are made directly when buffers are updated.

Important interactions:
- Uses `UFS_WAPBL_BEGIN/END`, `UFS_BALLOC`, `UFS_UPDATE`, `quota2_bwrite`, and byte-swap helpers.
- Shares `dqlock` with common dquot code to protect headers/lists and follows `dq_interlock -> dqlock` lock order.
- Uses `ufsmount` quota2 fields `umq2_bsize` and `umq2_bmask`.

Notable behavior and risks:
- Cursor iteration is two-pass: first gather keys under list protection, then fetch values by key without holding conflicting locks.
- If the quota2 hash size changes during cursor iteration, `EDEADLK` forces callers to restart.
- Corrupt quota headers or impossible entry offsets panic rather than returning ordinary I/O errors.
