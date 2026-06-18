# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1.c

Purpose: implements fsck pass 1, scanning all discoverable inodes, validating inode fields and extent-backed data, building in-memory accounting for links/directories/files/clusters, and reconciling inode and cluster allocation bitmaps.

Read coverage: complete file read, 1,572 lines.

Key responsibilities:
- Scans inodes with `ocfs2_open_inode_scan()` / `ocfs2_get_next_inode()`.
- Validates active inode basics: generation, `i_blkno`, root directory type, `i_dtime`, inline-data/refcount feature compatibility, type counters, link-count bookkeeping, local allocs, and truncate logs.
- Tracks directory inodes, regular inodes, directory parent state, link counts from inodes, directory blocks, file type counts, inline counts, tree depth counts, reflink counts, and duplicate cluster discovery.
- Validates symlink target storage, including fast symlink inline data, slow symlink NUL termination, target length, and `i_size`.
- Checks extent trees and directory index trees, marking metadata/data clusters through extent helpers and scheduling corrupt directory indexes for reset.
- Marks local alloc reserved clusters and truncate-log clusters as allocated so global allocation reconciliation preserves recoverable state.
- Reconciles global cluster bitmap against `ost_allocated_clusters`, including backup superblock exceptions.
- Writes corrected inode allocator bitmaps if inode validity differs from allocator chain state.

Important entry points:
- `o2fsck_pass1()` is the pass driver.
- `o2fsck_verify_inode_fields()` validates and classifies each dinode.
- `o2fsck_check_blocks()` validates file data, directory blocks, inline data, sparse/non-sparse size and cluster counts.
- `verify_local_alloc()` and `verify_truncate_log()` validate slot-local recovery structures.
- `mark_local_allocs()` and `mark_truncate_logs()` preserve allocated accounting for unreplayed recovery metadata.
- `write_cluster_alloc()` and `write_inode_alloc()` commit allocator reconciliation.
- `o2fsck_free_inode_allocs()` releases cached inode allocators created by pass 0.

Dependencies:
- Uses pass 0 cached inode allocators, directory block and parent trackers, inode-count maps, extent checking, xattr checking, refcount checking, libocfs2 inode scans, block iteration, chain allocator APIs, and backup superblock helpers.

Risk and edge cases:
- Invalid inodes are cleared by dropping `OCFS2_VALID_FL`, but comments note full freeing of attached data is incomplete.
- Duplicate cluster detection lazily allocates `ost_duplicate_clusters`; if allocation fails, fsck aborts via signal.
- For sparse files, `i_size` may legitimately exceed allocated extents; the code only corrects sizes smaller than visible data.
- Directory index corruption can be reset for later rebuild; inline directories are handled as directory blocks at the inode block itself.
- Local allocs and truncate logs are not fully replayed here; they are accounted as allocated and handled later/recovery-aware.
