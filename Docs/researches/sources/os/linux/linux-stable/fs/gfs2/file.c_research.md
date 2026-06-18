# File Research: sources/os/linux/linux-stable/fs/gfs2/file.c

## Scope

This file implements GFS2 VFS file and directory file operations: seeking, directory iteration, file attributes, ioctls, mmap fault handling, open/release, fsync, direct and buffered read/write paths, fallocate/punch-hole dispatch, splice write hints, and optional DLM-backed POSIX/flock locking.

## Public And Internal APIs Covered

- VFS file ops exported as `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, and `gfs2_dir_fops_nolock`.
- File attribute API: `gfs2_fileattr_get()`, `gfs2_fileattr_set()`, `gfs2_set_inode_flags()`.
- File lifecycle: `gfs2_open_common()`, `gfs2_open()`, `gfs2_release()`.
- I/O entry points: `gfs2_file_read_iter()`, `gfs2_file_write_iter()`, direct helpers, buffered write helper, `gfs2_fsync()`.
- MM integration: `gfs2_mmap()`, `gfs2_fault()`, `gfs2_page_mkwrite()`.
- Space management front end: `gfs2_fallocate()` and `__gfs2_fallocate()`.
- DLM-only locking: `gfs2_lock()` for POSIX locks and `gfs2_flock()` for flock locks.

## Control Flow And Behavior

- `gfs2_llseek()` takes the inode glock for `SEEK_END`, delegates hole/data seeks to inode helpers, and avoids glock acquisition for seek modes that do not need size or block mapping.
- `gfs2_readdir()` acquires the directory inode glock shared and delegates to `gfs2_dir_read()`.
- File flags translate between VFS `FS_*` flags and on-disk `GFS2_DIF_*` bits. Changing `GFS2_DIF_JDATA` flushes and waits page cache, truncates cached pages, adjusts ordered-data inode state, updates the dinode in a transaction, and resets address-space operations.
- `gfs2_page_mkwrite()` takes the inode glock exclusive, checks EOF, updates times, marks the glock dirty, un-stuffs inline files when needed, reserves quota and rgrp space, starts a transaction, allocates backing blocks via iomap, and returns with the folio locked and dirty on success.
- Direct read/write run under deferred glock mode and disable/fence page faults to avoid fault recursion while holding cluster locks. On `-EFAULT`, they drop the glock, fault user pages in manually, and retry. Direct writes beyond EOF fall back to buffered I/O.
- Buffered writes take the inode glock exclusive, fault pages in before lock acquisition where possible, use iomap buffered write ops, and special-case writes to the rindex inode by also locking the statfs inode.
- `gfs2_file_write_iter()` serializes with `inode_lock()`, performs generic write checks and privilege stripping, then routes direct writes through direct plus buffered fallback or buffered writes with timestamp updates and write sync handling.
- Fallocate only supports punch hole and keep-size allocation. Journaled data files reject fallocate except for the rindex inode. Allocation is chunked by rgrp/quota limits and zeroes newly allocated blocks.
- DLM POSIX locking delegates to `dlm_posix_*` under the lockspace semaphore. DLM flock locking uses per-file `gfs2_file::f_fl_gh` holders on `gfs2_flock_glops` glocks and coordinates with VFS local lock state.

## State And Data Structures

- Uses `gfs2_inode` fields `i_gl`, `i_diskflags`, `i_sizehint`, `i_res`, and `i_flags` including `GIF_SW_PAGED`.
- Per-open `struct gfs2_file` stores a mutex and flock holder.
- Allocation paths use `gfs2_alloc_parms`, quota data, rgrp reservations, transaction block reservations, and glock dirty state.
- File operation tables differ by DLM lock support: DLM builds install `.lock` and `.flock`; nolock builds use `generic_setlease`.

## Dependencies

- VFS/MM/iomap APIs: file ops, inode locks, folios, page faults, iomap direct and buffered I/O, fsync, fiemap-related seek helpers via inode.c, and fileattr APIs.
- GFS2 subsystems: glocks, glops, bmap/iomap allocation, quota, rgrp, transactions, metadata I/O, log flushing, directory reading, and punch-hole implementation.

## Risks And Invariants

- Page faults must not recurse into GFS2 while glocks are held; the direct and buffered paths carefully disable or pre-fault user memory.
- Direct I/O semantics require buffered fallback pages to be synced and invalidated before reporting combined progress.
- JDATA flag transitions require cache flush/truncation and address-space-op switching; stale page-cache state would violate data mode semantics.
- Fallocate reservation math must match quota/rgrp/metadata reservation ownership.
- Flock holder lifetime is protected by `file->f_lock`, `f_fl_mutex`, and an extra glock reference to avoid sleeping under spinlock during final put.
