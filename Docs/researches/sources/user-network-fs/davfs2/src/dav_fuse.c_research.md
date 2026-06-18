<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/dav_fuse.c -->
# Research: sources/user-network-fs/davfs2/src/dav_fuse.c

Purpose: FUSE kernel protocol v7 message loop and translation layer. It reads binary FUSE requests from `/dev/fuse`, maps them to `dav_*` cache calls, and writes binary replies.

Important APIs/functions: public `dav_fuse_loop()`. Static handlers include `fuse_access`, `fuse_create`, `fuse_getattr`, `fuse_init`, `fuse_lookup`, `fuse_mkdir`, `fuse_mknod`, `fuse_open`, `fuse_read`, `fuse_release`, `fuse_rename`, `fuse_setattr`, `fuse_stat`, `fuse_write`, plus helpers `write_dir_entry` and `set_attr`.

Control flow: `dav_fuse_loop` allocates a shared buffer, registers `write_dir_entry` with cache, then uses `select()` on the FUSE device. Timeouts trigger `dav_tidy_cache`; FUSE opcodes dispatch to handlers or return `ENOSYS` for unsupported operations. The loop maps FUSE root node ID 1 to the real `dav_node *` root captured during `FUSE_INIT`. On termination request, it forks `/bin/umount -il` on Linux or `/sbin/umount -v` on FreeBSD.

State and persistence: state is process-local: `buf_size`, `buf`, translated root pointer, debug flag, and idle-loop timing. Persistence is delegated to `cache.c`.

Dependencies/integration: depends on `fuse_kernel.h` structures, `cache.h` public API, `kernel_interface.h`, POSIX `select/read/write`, and syslog/gettext. `write_dir_entry` emits `struct fuse_dirent` records for directory cache files.

Risks: FUSE message parsing is manual and buffer-size-sensitive. Node IDs are raw pointers, so stale or forged IDs rely on cache validation. `fuse_read` returns `len + header` even if `dav_read` set an error, so negative/uninitialized `len` paths deserve review. Write loops add `w` even when `write()` fails, which can corrupt counters. Unsupported xattrs/symlinks/links are explicit functional gaps.

Test signals: FUSE protocol smoke tests for lookup/getattr/open/read/write/release/readdir/create/rename/setattr/statfs, malformed size requests, unmount signal path, idle cache tidy behavior, and unsupported opcode error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/dav_fuse.c -->
