# File Research: sources/os/linux/linux/fs/vboxsf/file.c

## Purpose
Implements vboxsf regular file operations, pagecache address-space operations, mmap setup, open-handle tracking, and symlink target reading.

## Main Functions
- Handle management:
  - `vboxsf_create_sf_handle()`: wraps a host handle, records access flags, and links it onto the inode handle list.
  - `vboxsf_release_sf_handle()` / `vboxsf_handle_release()`: remove and close host handles via kref.
- File operations:
  - `vboxsf_file_open()`: translates Linux open flags to SHFL create/access flags and opens or creates the host file.
  - `vboxsf_file_release()`: writes back dirty pages before closing the handle.
  - `vboxsf_file_mmap_prepare()` and `vboxsf_vma_close()`: install filemap mmap ops and force writeback when VMAs close.
  - `vboxsf_reg_fops`: generic read/write, mmap, open/release, splice, and noop fsync.
- Address-space operations:
  - `vboxsf_read_folio()`: reads a page from the host handle and zero-fills the tail.
  - `vboxsf_get_write_handle()`: finds a writable host handle for writeback.
  - `vboxsf_writepages()`: writes dirty folios using an open writable handle.
  - `vboxsf_write_end()`: writes copied bytes to the host, updates size, and marks full folios uptodate when appropriate.
  - `vboxsf_reg_aops`: hooks read, writeback, dirtying, simple write begin/end, migration.
- Symlinks:
  - `vboxsf_get_link()`: asks the host for symlink target.
  - `vboxsf_lnk_iops`: exposes `get_link` and fileattr query.

## Important Design Points
- Open flag mapping preserves read/write/append access and uses SHFL result codes because host API return status alone is not enough.
- The driver has no host change notifications, inode generation, or file locking support. It relies on open-time/stat-time revalidation in `utils.c`.
- Guest writes are pushed on close and VMA close so host-side readers can see updates.
- Writeback requires a still-open writable handle; if no such handle exists, `writepages()` returns `-EBADF`.
- Partial writes do not mark folios uptodate unless the whole folio was written.

## Cross-File Relationships
- Uses host read/write/create/close/readlink wrappers from `vboxsf_wrappers.c`.
- Uses `vboxsf_path_from_dentry()` and inode state from `utils.c`/`vfsmod.h`.
- `vboxsf_reg_aops` is installed by `vboxsf_init_inode()` in `utils.c`.

## Risks / Review Notes
- Cache coherency with host-side modifications is limited; read_iter deliberately relies only on revalidation before/open rather than per-read stats.
- Writeback can fail if dirty pages outlive writable handles.
- `noop_fsync` means fsync does not issue an explicit host flush here.
