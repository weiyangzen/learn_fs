# File Research: sources/os/linux/linux/fs/xfs/scrub/xfile.c

Implements XFS scrub “xfile” temporary swappable memory using an unlinked shmem file as a page-cache-backed staging area.

Key elements:
- `xfile_create` allocates an `xfile`, creates a kernel shmem file with `VMA_NORESERVE`, assigns a separate inode lockdep class, and forces non-highmem backing pages via `mapping_set_gfp_mask(..., GFP_KERNEL)`.
- `xfile_destroy` restores the inode lock class, drops the file reference, and frees the wrapper.
- `xfile_load` reads directly from shmem folios, returning zeroes for sparse regions and treating errors/short reads as `-ENOMEM`.
- `xfile_store` grows `i_size` before page allocation, copies caller data into folios, marks them dirty, and treats short writes as allocation failure.
- `xfile_seek_data` delegates to `vfs_llseek(..., SEEK_DATA)`.
- `xfile_get_folio` returns a locked folio for a range that must fit within one folio; optionally allocates with `XFILE_ALLOC`.
- `xfile_put_folio` unlocks and drops the folio.
- `xfile_discard` truncates shmem page cache over a byte range.

Dependencies:
- Uses tmpfs/shmem internals: `shmem_kernel_file_setup`, `shmem_get_folio`, `shmem_truncate_range`.
- Uses scrub allocation flags and tracing from `scrub/scrub.h`, `scrub/xfile.h`, `scrub/trace.h`.
- Uses NOFS scopes around shmem page cache access.

Research notes:
- Caller is responsible for concurrency; VFS inode/freezer locking is intentionally bypassed.
- The file is never exposed to userspace and must be released with `xfile_destroy`.
- Error policy deliberately collapses I/O and allocation failures to `-ENOMEM`, because this abstraction is treated as temporary memory.
- `xfile_store` and `xfile_get_folio(XFILE_ALLOC)` update `i_size` before allocation so shmem will instantiate folios.
