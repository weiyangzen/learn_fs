# File Research: sources/os/linux/linux-stable/fs/ocfs2/file.c

Purpose: Implements OCFS2 VFS file and directory operations, file-private lock state, fsync, atime updates, setattr/getattr/permission, file size changes, allocation extension, hole punching, fallocate, read/write iteration, seeking, and reflink remapping.

Read coverage: complete file read, 2893 lines.

Key structures and state:
- Uses `struct ocfs2_file_private` per open file for directory cookies, flock lock resource state, and file pointer backreferences.
- Coordinates VFS inode state with dinode buffer contents, OCFS2 inode private state, quota state, extent trees, refcount trees, page cache, and journal transactions.
- File operation tables provide normal and no-cluster-posix-lock variants for files and directories.

Major logic:
- Open/release paths allocate/free file-private state, initialize flock lock resources, maintain open counts, handle direct-open flags, and initialize quotas for writers.
- `ocfs2_sync_file()` waits on file data, completes the relevant JBD2 transaction, and issues a block-device flush if barriers require it.
- Atime helpers decide when clustered atime updates are needed and journal atime changes without relying on broad inode locks.
- Size update helpers journal dinode size, blocks, ctime, and mtime changes.
- Truncate paths CoW partial refcounted clusters, zero partial clusters, update i_size before allocation removal, drop page cache, remove extents, schedule truncate-log flushing, and attempt refcount-tree removal when empty.
- Extend paths allocate clusters for non-sparse files, zero newly exposed allocated ranges, convert inline data to extents when needed, and update size.
- `ocfs2_setattr()` handles size changes, ownership/mode/time changes, quota transfers, ACL chmod follow-up, recursive cluster-lock tracking, and rw-lock coverage for truncation/extension.
- Fallocate and reservation ioctls allocate unwritten extents or remove byte ranges through common change-file-space logic.
- Hole punching handles inline data, refcount CoW at range edges, partial-cluster zeroing, extent-tree walking from right to left, and page-cache truncation of fully removed clusters.
- Write preparation removes suid/sgid when necessary, checks NOWAIT overwrite eligibility, CoWs refcounted ranges, and upgrades from PR to EX metadata locks only when needed.
- Read/write iterators wrap generic I/O with OCFS2 rw locks, metadata locks, atime refresh, direct-I/O coherency rules, NOWAIT restrictions, and async direct-I/O lock handoff.
- `ocfs2_file_llseek()` supports SEEK_SET/CUR/END/DATA/HOLE with inode locking where size or extent state is needed.
- `ocfs2_remap_file_range()` implements reflink/dedupe remapping with dual-inode locking, allocation semaphores, destination page-cache invalidation, extent-map invalidation, and destination size update.

Important entry points:
- File operations: `ocfs2_file_open()`, `ocfs2_file_release()`, `ocfs2_sync_file()`, `ocfs2_file_read_iter()`, `ocfs2_file_write_iter()`, `ocfs2_file_splice_read()`, `ocfs2_file_llseek()`, `ocfs2_fallocate()`, `ocfs2_remap_file_range()`.
- Inode operations: `ocfs2_setattr()`, `ocfs2_getattr()`, `ocfs2_permission()`.
- Size/allocation helpers: `ocfs2_set_inode_size()`, `ocfs2_simple_size_update()`, `ocfs2_truncate_file()`, `ocfs2_add_inode_data()`, `ocfs2_extend_no_holes()`, `ocfs2_zero_extend()`, `ocfs2_remove_inode_range()`, `ocfs2_change_file_space()`.
- Exported operation tables: `ocfs2_file_iops`, `ocfs2_special_file_iops`, `ocfs2_fops`, `ocfs2_dops`, `ocfs2_fops_no_plocks`, `ocfs2_dops_no_plocks`.

Concurrency and lifetime:
- Uses VFS `inode_lock`, OCFS2 RW DLM locks, metadata DLM locks, and `ip_alloc_sem` in carefully ordered combinations.
- Truncate/setattr waits for direct I/O before taking cluster locks to avoid deadlocks with DIO completion.
- Direct I/O can hand RW-lock release to async completion; buffered async write queuing is BUG-checked because lock coverage would be wrong.
- NOWAIT support is limited to direct I/O and requires trylocks plus overwrite-only mapping checks.
- FIle-private flock resources are dropped and freed on release or directory close.
- Recursive inode-lock tracker paths prevent PR-to-EX upgrades within the same task.

Important dependencies:
- Extent allocation/mutation, truncate log, refcount tree CoW/reflink, inline-data conversion, quota operations, ACL chmod, journaling, ordered data tracking, inode refresh/locking, mmap preparation, ioctl handling, VFS generic I/O helpers, FIEMAP/seek helpers, and block zeroout/flush APIs.

Risk and edge cases:
- Partial-cluster zeroing is subtle because OCFS2 clusters can exceed page size and reflinked cluster edges must be CoWed before zeroing.
- Hole punching walks extent records from right to left and must keep path state, truncate bounds, and delayed deallocation synchronized.
- Write paths must remove suid/sgid before generic write to avoid recursive cluster locking through setattr.
- Size extension with sparse allocation still needs zeroing of already allocated ranges between old and new size.
- Direct-I/O coherency depends on mount options and whether the write is append or unaligned async.
- Operation tables must stay paired between normal and no-plock variants except for POSIX lock hooks.
