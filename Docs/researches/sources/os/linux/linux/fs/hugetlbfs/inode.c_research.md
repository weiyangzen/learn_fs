# File Research: sources/os/linux/linux/fs/hugetlbfs/inode.c

Full hugetlbfs implementation: a pseudo filesystem whose file contents are backed by hugetlb pages. It provides mount option parsing, inode creation, mmap/read/fallocate/truncate behavior, reservation accounting, internal kernel mounts for each hugepage hstate, and exported setup helpers for System V shared memory and similar users.

Main interfaces:
- `hugetlbfs_file_mmap()` validates hugepage alignment, installs hugetlb VMA operations, reserves pages, and extends file size for writable mappings.
- `hugetlb_get_unmapped_area()` enforces hugepage-aligned lengths and fixed addresses.
- `hugetlbfs_read_iter()` reads from hugetlb folios, returns zero-filled holes, and avoids raw HWPOISON subpages.
- `remove_inode_hugepages()`, `hugetlb_vmtruncate()`, and `hugetlbfs_punch_hole()` coordinate page-cache removal, VMA unmapping, reserve-map updates, and partial-page zeroing.
- `hugetlbfs_fallocate()` supports hole punching and preallocation by allocating huge folios through a pseudo VMA.
- `hugetlbfs_setattr()` enforces hugepage-aligned sizes and memfd seals.
- `hugetlbfs_get_inode()` creates regular, directory, symlink, and special inodes with reservation maps only where page allocations can occur.
- `hugetlb_file_setup()` creates pseudo hugetlbfs files for kernel consumers and enforces hugepage shm permission checks.

Mount behavior:
- Parses `uid`, `gid`, `mode`, `size`, `min_size`, `nr_inodes`, and `pagesize`.
- Supports byte sizes and percentages for subpool limits.
- `hugetlbfs_fill_super()` creates `hugetlbfs_sb_info`, optional subpool, root dentry, hugepage block size, and non-stacking depth.
- `init_hugetlbfs_fs()` creates the inode cache, registers the filesystem, and mounts one internal hugetlbfs instance per hstate.

Accounting and lifecycle:
- Inode allocation/deallocation maintains optional inode limits.
- Superblock teardown releases hugepage subpools.
- Eviction removes hugepages, releases reservation maps, and clears the inode.
- Migration support preserves hugetlb subpool attachment.

Concurrency and risk:
- Truncate, hole punch, and fallocate depend on `hugetlb_fault_mutex_table`, `i_mmap_rwsem`, hugetlb VMA locks, folio locks, and inode locks in carefully documented order.
- Reserve-map and subpool counts must remain synchronized with page-cache deletion.
- mmap and fallocate paths must preserve hugepage alignment and overflow checks.
- HWPOISON handling in reads deliberately returns partial safe data or `-EIO`.
