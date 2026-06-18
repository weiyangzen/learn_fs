# File Research: sources/local-fs/f2fs-tools/fsck/quotaio.c

Purpose: generic quota-file IO wrapper for F2FS quota operations.

Key behavior:
- Defines quota type string extensions for user/group/project.
- Exposes global quota-file size-check state: `cur_qtype`, `qf_last_blkofs`, `qf_szchk_type`, and `qf_maxsize`.
- `quota_type2name()` maps quota type enum to text.
- `update_grace_times()` starts or clears block/inode grace timers based on soft-limit violations.
- `quota_write_nomount()` writes to a quota inode via `f2fs_write()`, tracks logical file size, and reports short writes as `-EIO`.
- `quota_read_nomount()` reads from a quota inode via `f2fs_read()`.
- `quota_file_open()` initializes a `quota_handle`, selects VFS v1 ops (`quotafile_ops_2`), verifies format, runs format init, and stores allocated handles in the quota context.
- `quota_file_create()` initializes a new quota file handle and calls V2 `new_io`.
- `quota_file_close()` writes dirty info, calls format close hook if any, optionally updates inode filesize, and frees context-owned handles.
- `get_empty_dquot()` allocates and zeroes a quota record with `dq_id = -1`.

Important dependencies:
- Delegates format behavior to `quotaio_v2.c`.
- Uses F2FS inode read/write helpers and quota context from fsck state.

Risk notes:
- Read/write callback type is `unsigned int`, but write failure paths return negative errno values through it, relying on callers comparing against expected sizes.
- `quota_file_open()` assumes `fsck->qctx` is initialized if it needs to allocate/store handles.
