# sources/user-network-fs/libfuse/include/fuse.h

## Purpose
`fuse.h` is the public high-level libfuse API header. It defines the path-oriented operation table, high-level configuration, context accessors, event-loop helpers, service-main wrapper for service mode, cache/poll helpers, and the stacking/module API used by FUSE filesystems.

## Important APIs, Types, and Functions
Important types include opaque `struct fuse`, `enum fuse_readdir_flags`, `enum fuse_fill_dir_flags`, `fuse_fill_dir_t`, `struct fuse_config`, `struct fuse_operations`, `struct fuse_context`, and opaque `struct fuse_fs`. `struct fuse_config` contains uid/gid/mode rewriting, entry/negative/attr timeouts, interrupt settings, inode remembering, hard-remove, inode reporting, direct I/O, kernel/auto cache, nullpath support, masks, no-rofd-flush, and `parallel_direct_writes`. `struct fuse_operations` defines callbacks from basic metadata and namespace operations through modern handlers such as `write_buf`, `read_buf`, `flock`, `fallocate`, `copy_file_range`, `lseek`, `statx`, and `syncfs`. Lifecycle helpers include `fuse_main`, `fuse_new`, `fuse_mount`, `fuse_unmount`, `fuse_loop`, `fuse_loop_mt`, `fuse_exit`, and `fuse_destroy`.

## Control Flow
Most high-level filesystems either call `fuse_main()` or manually call `fuse_new()`, `fuse_mount()`, and an event loop. `fuse_main()` parses options, installs signal handlers, creates the handle, registers operations, and runs the selected loop. During initialization, libfuse passes `struct fuse_conn_info` and mutable `struct fuse_config` to the filesystem's `init` callback; operation callbacks then receive paths and optional `struct fuse_file_info`. Filesystems return zero or negative errno values from callbacks. In FUSE 3.19 and newer, `fuse_service_main()` wraps service-mode startup from an accepted `struct fuse_service`.

## State and Persistence
The header defines API contracts rather than storing state. High-level runtime state lives in the opaque `struct fuse`, `struct fuse_fs` layers, operation private data, request contexts, and kernel caches controlled by `fuse_config`. Persistence is entirely filesystem-specific. Cache-related config fields are central because they decide how long kernel lookup, attribute, negative, and file-data state survive.

## Dependencies and Integration Points
`fuse.h` includes `fuse_common.h` and POSIX stat/statvfs/uio/time headers. It integrates high-level APIs with lower-level sessions through `fuse_get_session()`, with polling through `fuse_notify_poll()`, with cache invalidation through `fuse_invalidate_path()`, with cleanup of remembered inodes, and with stackable modules through `fuse_fs_*` wrappers and `FUSE_REGISTER_MODULE`.

## Risks
This header is ABI-sensitive; `struct fuse_config` explicitly warns that new options must be appended. Callback semantics contain many traps: `flush` is not `fsync`, `release` return values are ignored, writeback cache can cause reads on write-only opens and kernel-handled `O_APPEND`, `hard_remove` changes unlinked-open-file behavior, `parallel_direct_writes` can corrupt data if the filesystem lacks its own synchronization, and context pointers are valid only during the operation. Version-dependent `ioctl` signatures and `fuse_loop_mt` macros require matching `FUSE_USE_VERSION`.

## Test Signals
Header-level validation includes compiling representative high-level filesystems across supported `FUSE_USE_VERSION` values, exercising all optional callbacks through the `fuse_fs_*` wrapper API, checking C++ linkage, and verifying service-main availability at version 3.19+. Runtime tests should focus on cache options, readdir offsets/readdirplus, open/read/write/flush/release ordering, lock behavior, poll notifications, statx, copy-file-range, lseek, and syncfs behavior on fuseblk servers.
