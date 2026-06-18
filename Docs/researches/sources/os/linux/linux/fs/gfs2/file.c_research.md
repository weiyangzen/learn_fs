# File Research: sources/os/linux/linux/fs/gfs2/file.c

## Scope

Implements GFS2 file and directory VFS operations: llseek, readdir, inode file attributes, ioctls, mmap faults, open/release, fsync, buffered/direct reads and writes, fallocate/punch-hole handling, splice-write size hints, and optional DLM-backed POSIX/flock locking.

## Public And Internal APIs Covered

- File operation tables: `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, `gfs2_dir_fops_nolock`.
- Attribute APIs: `gfs2_fileattr_get()`, `gfs2_fileattr_set()`, `gfs2_set_inode_flags()`.
- File lifecycle: `gfs2_open_common()`, `gfs2_open()`, `gfs2_release()`.
- I/O paths: `gfs2_file_read_iter()`, `gfs2_file_write_iter()`, direct read/write helpers, buffered write helper.
- MM paths: `gfs2_mmap()`, `gfs2_fault()`, `gfs2_page_mkwrite()`.
- Allocation paths: `gfs2_fallocate()`, `__gfs2_fallocate()`, `fallocate_chunk()`.
- DLM locking paths: `gfs2_lock()`, `gfs2_flock()`, `do_flock()`, `do_unflock()`.

## Control Flow And Behavior

- `gfs2_llseek()` takes the inode glock for `SEEK_END`, delegates data/hole seeks to inode helpers, and avoids glock acquisition for seek modes that do not need inode size or block mapping.
- `gfs2_readdir()` acquires the directory inode glock shared before calling `gfs2_dir_read()`.
- File flags map between VFS `FS_*` flags and on-disk `GFS2_DIF_*` flags. JDATA changes flush/wait/truncate cached pages, update ordered-data state, commit a dinode transaction, and reset address-space operations.
- `gfs2_page_mkwrite()` holds the inode glock exclusive, validates EOF, updates times, marks the glock dirty, unstuffs inline files when needed, reserves quota/rgrp space, begins a transaction, allocates backing blocks through iomap, and returns with the folio locked and dirty on success.
- Direct I/O uses deferred glock mode, disables or fences page faults while cluster locks are held, manually faults user pages on `-EFAULT`, and retries. Direct writes past EOF fall back to buffered I/O.
- Buffered writes acquire the inode glock exclusive, pre-fault user pages when possible, write through iomap, and lock the statfs inode when writing the rindex inode.
- `gfs2_file_write_iter()` serializes through `inode_lock()`, runs generic write checks and privilege stripping, dispatches direct or buffered writes, and performs sync/writeback handling.
- Fallocate supports punch-hole and keep-size allocation; journaled data files reject normal fallocate except for the rindex inode.
- DLM POSIX locks delegate to `dlm_posix_*`; DLM flock locks use per-open `gfs2_file::f_fl_gh` holders on `gfs2_flock_glops` glocks.

## State And Invariants

- Uses `gfs2_inode` fields `i_gl`, `i_diskflags`, `i_sizehint`, `i_res`, and `i_flags` including `GIF_SW_PAGED`.
- Per-open `struct gfs2_file` stores flock mutex/holder state.
- Page-fault recursion while holding glocks is explicitly avoided.
- Direct I/O buffered fallback must be synced and invalidated before reporting combined progress.
- Fallocate reservation math must remain consistent with quota, rgrp, metadata, and transaction reservations.
