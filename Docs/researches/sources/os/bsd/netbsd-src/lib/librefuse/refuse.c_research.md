# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse.c

This is the main ReFUSE implementation that maps high-level FUSE operations onto NetBSD puffs. It defines per-node state (`struct refusenode`), directory-buffer handling, FUSE context management, puffs vnode callbacks, setup/teardown, mount/unmount, loop, destroy, version/pkg helpers, and unsupported compatibility stubs.

The puffs callbacks translate lookup, getattr, setattr, readlink, mknod, mkdir, create, remove, rmdir, symlink, rename, link, open, close, read, write, readdir, reclaim, sync, statvfs, and unmount into `fuse_fs_*` calls. FUSE callbacks return negative errno-style results, while puffs expects positive errno values, so the file repeatedly negates or normalizes results. It also caches open `fuse_file_info` per puffs node and slurps complete directories into a puffs-formatted dirent buffer.

Setup parses FUSE command-line options, handles help/version, creates a `struct fuse`, initializes puffs operations, installs signal handlers, daemonizes through puffs, and mounts. Context handling uses pthread-specific storage when `MULTITHREADED_REFUSE` is enabled, otherwise a static context.

Risks: several comments mark incomplete areas, including proper multithreaded loop support, clean destruction/quiescence, `getgroups`, cache cleanup, and exact create/open semantics. Directory offset handling is acknowledged as unclear, fake inode allocation is not thread-safe, and close returns raw FUSE callback status rather than consistently converting negative errno in the same style as most other callbacks.
