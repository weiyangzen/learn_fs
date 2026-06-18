<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.c -->
# Research: sources/user-network-fs/davfs2/src/kernel_interface.c

Purpose: privileged setup of the FUSE kernel interface. It opens `/dev/fuse`, loads the kernel module if necessary, sizes buffers, mounts the FUSE filesystem, and restores the original effective UID.

Important APIs/functions: public `dav_init_kernel_interface(int *dev, size_t *buf_size, const char *url, const char *mpoint, const dav_args *args)`. FreeBSD-only helpers `add_iovec_opt` and `free_iovec` build `nmount()` iovec options.

Control flow: temporarily `seteuid(0)`, open `/dev/fuse` nonblocking, fork `modprobe fuse` on Linux or `kldload fusefs` on FreeBSD if open fails, retry after a short wait, enforce buffer size at least `FUSE_MIN_READ_BUFFER + 4096`, then mount. Linux builds a mount data string with fd, rootmode, user_id, group_id, `allow_other`, and `max_read`; FreeBSD uses `nmount` with iovec options. On success, restores original euid.

State and persistence: returns an open FUSE device fd and updated buffer size. Kernel mount table state is changed by `mount()`/`nmount()`.

Dependencies/integration: called by mount helper after parsing `dav_args`; pairs with `dav_fuse_loop` for ongoing request handling. Depends on root privileges, `/dev/fuse`, module loaders, system mount APIs, and `defaults.h` device path.

Risks: mount data includes `allow_other`, making local permission handling in `cache.c` critical. Privilege switching failures abort. Module-loading paths are hard-coded. Errors call `ERR`, so this function terminates the program on many failures. Mount options and root mode must match security documentation.

Test signals: root and unprivileged mount flows, missing `/dev/fuse` with module loading, FreeBSD/Linux mount path tests, buffer-size negotiation, euid restoration on success/failure, and mount option inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.c -->
