# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_vnops.c

Core vnode-backed file operation implementation. This file binds `struct fileops vnops` to vnode methods and supplies the shared helpers that filesystems rely on for open/close, read/write, offset locking, mount write suspension, truncation, mmap, fsync, range copy, allocation/deallocation, directory iteration, and vnode pair locking.

Key responsibilities:
- Fileops table: `vnops` maps file-layer operations to vnode-backed implementations: read/write via `vn_io_fault`, truncate, ioctl, poll, kqueue, stat, close, chmod/chown, sendfile, seek, mmap, fallocate, fspacectl, compare.
- Open/close path: `vn_open_cred()` drives name lookup and optional creation; `vn_open_vnode()` checks vnode type, access, MAC, `O_PATH`, FIFO locking, `VOP_OPEN()`, advisory locks, and writecount accounting; `vn_close1()` pairs close and writecount decrement.
- I/O path: `vn_rdwr()`, `vn_read()`, `vn_write()`, `vn_rdwr_inchunks()`, `vn_read_from_obj()`, and write-ioflag helpers manage VOP read/write calls, page-cache reads, direct/sync/dsync flags, sequential heuristics, and `posix_fadvise` state.
- Deadlock avoidance: `vn_io_fault1()`, `vn_io_fault_uiomove()`, and `vn_io_fault_pgmove()` avoid vnode lock order reversals caused by page faults during VOP read/write into userspace buffers.
- Offset synchronization: `foffset_lock()`, `foffset_unlock()`, `foffset_lock_pair()`, and UIO helpers serialize file offset updates with atomic or mutex-backed implementations depending on platform word size.
- Write suspension: `vn_start_write()`, `vn_start_secondary_write()`, `vn_finished_write()`, `vfs_write_suspend()`, `vfs_write_resume()`, and unmount suspension helpers coordinate writes against filesystem suspension.
- Metadata/file helpers: `vn_truncate_locked()`, `vn_statfile()`, `vn_ioctl()`, `vn_poll()`, `vn_chmod()`, `vn_chown()`, `vn_utimes_perm()`, `vn_mmap()`, `vn_fsync_buf()`, `vn_fsid()`.
- Copy and space management: `vn_copy_file_range()` chooses filesystem-specific or generic copy; `vn_generic_copy_file_range()` handles sparse copying, holes, zero scanning, timeouts, and output growth; `vn_fallocate()`, `vn_deallocate()`, and `vn_fspacectl()` wrap allocation/deallocation VOPs.
- Directory helpers: `vn_dir_next_dirent()` provides robust buffered directory iteration; `vn_dir_check_empty()` uses it to detect non-dot entries while ignoring whiteouts.
- Locking helpers: `_vn_lock()` handles doomed vnode behavior and delayed size updates; `vn_lock_pair()` avoids lock order reversal for two vnodes; `vn_lktype_write()` selects shared/exclusive write locking.

Important patterns:
- Range locks protect split I/O, truncation, copy-range, and no-page-fault I/O windows.
- Vnode writecount is carefully paired with opens, truncation, mmap, and failed-open cleanup.
- Generic copy-range preserves sparse files when possible by using `FIOSEEKDATA/FIOSEEKHOLE` or block zero detection.
- Mount write suspension is reference-counted and has special primary/secondary write accounting.
- Many helpers are exported for filesystem code, not just syscall code.

Research relevance:
- This is the primary file for understanding FreeBSD's common vnode operation semantics and the expectations imposed on filesystem VOP implementations.
- It complements `vfs_syscalls.c`: syscalls enter there, then common file/vnode mechanics are performed here.
