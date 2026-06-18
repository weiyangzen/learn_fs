# File Research: sources/os/linux/linux/fs/ocfs2/file.c

OCFS2 file operation implementation. This file owns file open/release state, fsync, atime updates, truncate/extend, setattr/getattr/permission, preallocation and hole punching, buffered/direct read/write locking, llseek, reflink remap, and the exported VFS operation tables.

Open and per-file state:
- `ocfs2_init_file_private()` allocates `struct ocfs2_file_private`, initializes its mutex and per-file flock DLM lock resource, and stores it in `file->private_data`.
- Regular file open initializes quotas for writers, rejects inodes marked deleted, records direct-open state, increments `ip_open_count`, and sets `FMODE_NOWAIT`.
- Release decrements open count, clears direct-open state when the last open closes, and drops the per-file flock lock resource.
- Directories use the same private state for directory cookies and flock support.

Fsync and atime:
- `ocfs2_sync_file()` writes dirty pages, completes the relevant JBD2 transaction, and issues a block-device flush when journal barriers require one.
- `ocfs2_should_update_atime()` implements noatime/nodiratime/relatime and OCFS2 atime quantum policy.
- `ocfs2_update_inode_atime()` updates only atime in a small journal transaction without using the broader dirty-inode helper.

Size updates, truncate, and extend:
- `ocfs2_set_inode_size()` updates VFS inode size, block count, ctime/mtime, and dinode state through `ocfs2_mark_inode_dirty()`.
- `ocfs2_simple_size_update()` wraps that in a transaction.
- `ocfs2_truncate_file()` handles shrink. It holds `ip_alloc_sem`, discards local allocation reservations, handles inline-data truncation, zeroes partial clusters, updates size before allocation removal, truncates page cache, commits extent-tree truncation, schedules truncate-log flush, and tries to remove an empty refcount tree.
- `ocfs2_orphan_for_truncate()` prepares a shrink so recovery can finish later; it CoWs a partial refcounted cluster when needed and zeroes the post-size cluster tail.
- `ocfs2_extend_file()` handles grow. Inline data may remain inline if the new size fits; otherwise inline data is converted to extents. Sparse files zero allocated ranges only; nonsparse files allocate clusters with `ocfs2_extend_no_holes()`.
- `ocfs2_extend_allocation()` locks allocators, reserves quota, starts/restarts journal transactions, adds extent-tree clusters, handles metadata/transaction restarts, and releases unused quota.

Zeroing:
- `ocfs2_zero_extend()` finds allocated, written ranges between old size and new size, CoWs refcounted extents, and zeroes them page by page.
- `ocfs2_write_zero_page()` uses block write helpers without logically exposing stale data and updates i_size temporarily so writeback does not drop dirty EOF pages.
- `ocfs2_zero_partial_clusters()` zeroes unaligned edges for hole punching/truncate, using disk zeroout beyond EOF where page-cache writes are unsuitable.
- Ordered-data files register zeroed ranges with JBD2 when needed.

Setattr/getattr/permission:
- `ocfs2_setattr()` validates attributes, initializes quota when ownership changes, serializes size changes with DIO wait and rw EX lock, uses inode lock tracker, handles truncate/extend, performs quota transfer, updates inode attributes in a transaction, and runs ACL chmod after mode changes.
- Recursive cluster-lock detection is logged because ACL paths can re-enter inode operations.
- `ocfs2_getattr()` revalidates inode state, fills stat data, reports at least one sector for inline-data files, and uses cluster size as preferred block size.
- `ocfs2_permission()` takes a PR metadata lock unless `MAY_NOT_BLOCK` is set.

Preallocation and hole punching:
- `ocfs2_allocate_unwritten_extents()` converts inline data when needed and allocates unwritten extents over holes.
- `ocfs2_remove_inode_range()` handles inline-data punching, CoWs partial refcounted edge clusters, zeroes partial clusters, walks extent leaves from right to left, removes btree ranges, truncates page cache, schedules truncate-log flush, and runs cached deallocations.
- `__ocfs2_change_file_space()` backs OCFS2 reservation ioctls and fallocate. It validates ranges, strips suid/sgid if needed, locks rw/meta/allocation state, allocates unwritten extents or removes ranges, optionally extends i_size, updates timestamps, and honors O_SYNC.
- `ocfs2_fallocate()` supports keep-size and punch-hole modes when unwritten extents are available.

Read/write:
- `ocfs2_prepare_inode_for_write()` obtains metadata locks and `ip_alloc_sem`, checks NOWAIT overwrite feasibility, strips suid/sgid under an EX metadata lock, and CoWs refcounted write ranges.
- `ocfs2_file_write_iter()` rejects buffered NOWAIT, serializes through `inode_lock`, takes the rw lock at EX or PR depending on direct/buffered/full-coherency/append mode, forces metadata EX lock for full-coherency direct I/O, runs generic write checks, prepares extents, converts unaligned async direct I/O to sync completion, and coordinates rw lock release with direct-I/O completion via `iocb->private`.
- `ocfs2_file_read_iter()` takes rw PR for direct I/O, refreshes inode/atime metadata, delegates to generic read, and defers rw unlock to DIO completion when queued.
- `ocfs2_file_splice_read()` refreshes metadata/atime before `filemap_splice_read()`.

Seeking and remap:
- `ocfs2_file_llseek()` handles SEEK_END under inode metadata lock and SEEK_DATA/SEEK_HOLE via extent-map logic.
- Directory llseek uses `generic_llseek_cookie()` with the per-file directory cookie.
- `ocfs2_remap_file_range()` implements reflink/dedupe remap. It requires refcount support, locks both inodes, validates eligibility, locks allocation maps, zaps destination page cache, remaps blocks, clears extent caches, and updates destination size/metadata.

Operation tables:
- `ocfs2_file_iops` and `ocfs2_special_file_iops` install setattr/getattr/permission/xattr/ACL/fileattr hooks.
- `ocfs2_fops` and `ocfs2_dops` include POSIX lock callbacks.
- `ocfs2_fops_no_plocks` and `ocfs2_dops_no_plocks` omit POSIX lock callbacks but keep flock support.

Important invariants and risks:
- Size-changing operations require careful ordering across inode rwsem, rw cluster lock, metadata lock, DIO wait, and `ip_alloc_sem`.
- Partial cluster zeroing is required to avoid stale data exposure on truncate, extend, and hole punch.
- Refcounted extents must be CoWed before partial overwrite or zeroing.
- NOWAIT is only supported where lock acquisition and overwrite checks can avoid blocking.
- DIO completion owns rw-lock release in queued async cases.
