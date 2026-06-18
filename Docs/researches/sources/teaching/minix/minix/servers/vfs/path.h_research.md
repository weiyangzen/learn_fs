# File Research: sources/teaching/minix/minix/servers/vfs/path.h

Defines the shared pathname lookup descriptor:

- `struct lookup` contains the mutable path buffer, VFS/FS lookup flags, desired `vmnt` and vnode lock modes, and output pointers for the locked `vmnt` and vnode.
- Used by `path.c`, `open.c`, `mount.c`, `protect.c`, and socket path handling to standardize lookup intent and returned locks.
- Callers must initialize it with `lookup_init` before use and set non-`TLL_NONE` lock modes before calling `advance`, `eat_path`, or `last_dir`.
