# File Research: sources/os/linux/linux-stable/fs/hugetlbfs/inode.c

This file implements hugetlbfs, a ramfs-like filesystem backed by hugetlb pages. It covers file mapping, read behavior, hugepage reservation accounting, inode creation, truncation, hole punching, fallocate, mount option parsing, internal kernel mounts, and filesystem registration.

Key responsibilities:
- Defines mount context state for hugepage hstate selection, size/min-size limits, inode limits, ownership, and mode.
- Parses mount options: `uid`, `gid`, `mode`, `nr_inodes`, `pagesize`, `size`, and `min_size`.
- Implements `hugetlbfs_file_mmap()` with hugepage-aligned offsets, overflow checks, reservation via `hugetlb_reserve_pages()`, and size growth on writable mappings.
- Implements `hugetlb_get_unmapped_area()` with hugepage alignment requirements.
- Provides `hugetlbfs_read_iter()`, which reads hugetlb folios from page cache, zero-fills holes, and avoids raw HWPOISON subpages.
- Rejects normal buffered write begin/end paths; file population occurs through mmap faults and fallocate-style allocation.
- Removes hugepages from page cache during truncate, eviction, and hole punch while coordinating with hugetlb fault mutexes and VMA locks.
- Implements `hugetlbfs_fallocate()` for both preallocation and `FALLOC_FL_PUNCH_HOLE`.
- Enforces seals for grow, shrink, and write/future-write constraints in `hugetlbfs_setattr()` and hole punching.
- Creates regular files, directories, symlinks, special files, and tmpfiles using simple filesystem helpers plus hugetlb-specific reservation maps.
- Tracks inode limits using `hugetlbfs_dec_free_inodes()` and `hugetlbfs_inc_free_inodes()`.
- Implements `statfs`, mount option display, superblock teardown, inode slab cache setup, and filesystem registration.

Important interactions:
- Depends on hugetlb MM APIs for hstate lookup, hugepage allocation, reservation, subpool creation, migration, page cache insertion, and VMA unmapping.
- Uses `simple_*` VFS helpers for directory behavior while adding hugetlb-specific inode setup and reservation maps.
- Maintains internal kernel mounts in `hugetlbfs_vfsmount[]`, one per hstate where possible.
- Exposes `hugetlb_file_setup()` for kernel users such as SysV shared memory with `SHM_HUGETLB`.

Notable invariants and risks:
- File sizes and offsets must be hugepage aligned for truncation and mapping.
- Reservation accounting is subtle: truncate and hole punch differ in how reserve maps are released.
- Hole punch must coordinate with page faults and VMAs to avoid retaining mapped pages for removed ranges.
- Internal hugetlbfs mounts for non-default hstates are optional; default hstate mount is required.
- `hugetlbfs_fill_super()` uses `kfree(sbinfo->spool)` on an allocation failure path even though normal teardown uses `hugepage_put_subpool()`; this is worth checking against the exact ownership semantics of `hugepage_new_subpool()` in this kernel tree.

Research notes:
- This file is the bridge between VFS file semantics and hugetlb memory accounting. The most important logic is not pathname handling but synchronization among page cache, VMA mappings, reservation maps, and subpool/global hugepage counts.
