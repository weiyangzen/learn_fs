# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kobj_vfs.c

Read completely: 199 lines.

Provides the VFS-backed object source for the kobj loader when `MODULAR` is enabled. `kobj_load_vfs()` opens a path with `vn_open()`, initializes a `kobj_t` as `KT_VNODE`, installs VFS read/close callbacks, and calls `kobj_load()`.

Core behavior:
- `kobj_read_vfs()` optionally allocates a buffer, or reads directly into already mapped text/data/rodata segment memory.
- Reads use `vn_rdwr()` with `IO_NODELOCKED`; short reads are treated as `EINVAL`.
- `kobj_close_vfs()` unlocks and closes the vnode.
- Paths without a slash are rejected with `ENOENT`.
- Non-modular builds return `ENOSYS`.

Risks and notes:
- DIAGNOSTIC builds verify non-allocated read targets lie inside dedicated text/data/rodata segments.
- `nochroot` controls whether `vn_open()` uses `NOCHROOT`.
