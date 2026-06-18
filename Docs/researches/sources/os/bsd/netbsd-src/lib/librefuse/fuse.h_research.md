# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse.h

This public header exposes ReFUSE's high-level FUSE compatibility API. It includes option, buffer, channel, legacy, poll, session, stat, statvfs, and utime-related headers, then defines version selection logic for many FUSE API generations.

Version handling is central. `FUSE_MAKE_VERSION` supports the historical `(maj * 10 + min)` encoding and the FUSE 3.10-era `(maj * 100 + min)` encoding. ReFUSE declares implementation support through `_REFUSE_MAJOR_VERSION_` 3 and `_REFUSE_MINOR_VERSION_` 10. User code is expected to define `FUSE_USE_VERSION`; if not, external users get a warning and default to the latest version. `FUSE_VERSION`, `FUSE_MAJOR_VERSION`, and `FUSE_MINOR_VERSION` are tied to `FUSE_USE_VERSION`.

Common structs include `fuse_file_info`, `fuse_conn_info`, `fuse_context`, `fuse_config`, `fuse_loop_config`, and `fuse_args`, plus FUSE capability flags, ioctl flags, and readdir/fill-dir flags. Common functions include loop/exit/context, daemonize, interrupted check, cache invalidation by path, version strings, group lookup, cleanup-thread helpers, cache cleanup, and the internal generic `__fuse_main`.

The bottom half includes all versioned compatibility headers unconditionally, then uses `#if FUSE_USE_VERSION` blocks to alias `fuse_operations`, fill-dir types, mount/unmount/new/destroy/setup/teardown/loop/parse/fs wrappers, and inline `fuse_main`/`fuse_new`/`fuse_setup` signatures for API versions 1.1 through 3.10. This preserves source compatibility for filesystems written against older FUSE APIs while routing implementation to version-suffixed ReFUSE entry points.
