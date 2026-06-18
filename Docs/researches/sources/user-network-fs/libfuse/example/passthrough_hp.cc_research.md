# sources/user-network-fs/libfuse/example/passthrough_hp.cc

## Purpose
`passthrough_hp.cc` is a high-performance C++ low-level passthrough filesystem. It mirrors a specified source directory, maintains its own inode map keyed by backing `(st_ino, st_dev)`, supports optional cache disabling, writeback cache, kernel FUSE passthrough mode, splice control, SELinux create contexts, direct I/O, and multi-threaded operation. It is intended as a production-quality template rather than a minimal demo.

## Important APIs, Types, and Functions
Key types are `SrcId`, `Inode`, `InodeMap`, and global `Fs fs`. `Inode` stores backing `fd`, source IDs, generation, passthrough `backing_id`, open count, atomic lookup count, and a mutex. `Fs` stores global config, source path, root inode, cache/pass-through flags, and a mutex. Important operations include `sfs_init`, `do_lookup`, `sfs_lookup`, `mknod_symlink`, `sfs_unlink`, `forget_one`, `do_readdir`, `sfs_create`, `sfs_tmpfile`, `sfs_open`, `do_passthrough_open`, `sfs_release`, `do_read`, `do_write_buf`, xattr handlers, and `assign_operations`.

## Control Flow
`parse_options()` uses cxxopts to parse source, mountpoint, debug, cache, splice, passthrough, SELinux, thread, clone-fd, direct-io, and mount options. `main()` resolves and validates the source directory, raises the file descriptor limit, opens the root with `O_PATH`, creates a low-level session, sets signal/fail handlers, daemonizes early, mounts, starts a teardown watchdog, and runs a single- or multi-threaded loop. Lookups open children with `O_PATH|O_NOFOLLOW`, validate that they stay on the source device and avoid `FUSE_ROOT_ID`, then insert/reuse `Inode` objects in `fs.inodes`. File opens create real read/write fds from `/proc/self/fd` or FreeBSD path info and may install a shared kernel passthrough backing file.

## State and Persistence
Persistent state is the backing source tree. Runtime state is substantial: a global inode map, per-inode fds, generation counters for recycled inodes, open counts, lookup counts, cached passthrough backing IDs, directory handles, and global mount behavior. With normal caching, timeout is 86400 seconds and the source is assumed to change only through the FUSE mount; `--nocache` sets timeout zero and includes unlink logic to close last-link fds before unlink to handle inode-number reuse. SELinux fscreate labels are staged per worker thread and immediately cleared after create-like syscalls.

## Dependencies and Integration Points
The file depends on `fuse_lowlevel.h`, `fuse_daemonize.h`, cxxopts, pthread/libc syscalls, syslog, resource limits, `/proc/self/fd` on Linux or `F_KINFO` on FreeBSD, and optional xattr support. It integrates with feature negotiation through `FUSE_CAP_PASSTHROUGH`, `FUSE_CAP_WRITEBACK_CACHE`, `FUSE_CAP_FLOCK_LOCKS`, `FUSE_CAP_SECURITY_CTX`, splice caps, `FUSE_CAP_DIRECT_IO_ALLOW_MMAP`, and `FUSE_CAP_NO_EXPORT_SUPPORT`. It uses `fuse_passthrough_open/close`, `fuse_req_get_payload()` for io_uring payloads, and `fuse_session_start_teardown_watchdog()`.

## Risks
Pointer-valued inode IDs require the pointed `Inode` to remain valid while the kernel may reference it; this is managed by lookup counts, so negative counts or incorrect forget handling aborts. Holding one fd per known dentry can exhaust descriptors despite `maximize_fd_limit()`. Cached mode can return stale or dangerous results if the source tree is modified outside the FUSE mount, and the header warns of possible data loss. `do_lookup()` returns `ENOTSUP` for mountpoints but does not close `newfd` on that path, which is a leak signal. Passthrough and direct I/O choices interact: read/write handlers treat unexpected fallback in passthrough mode as `EIO`.

## Test Signals
Exercise both default cached mode and `--nocache` while modifying the source through and outside the mount. Run xfstests-style create/unlink/rename/hardlink/readdirplus/open-after-unlink tests, descriptor-pressure tests, passthrough-capability fallback tests, SELinux create-label tests, direct-io mmap tests, and io_uring payload reads. Verify unmount and forced teardown do not leave backing IDs or fds open.
