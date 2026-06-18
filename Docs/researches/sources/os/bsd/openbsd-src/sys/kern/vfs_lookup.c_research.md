# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_lookup.c

Read completely: 880 lines.

Implements OpenBSD pathname resolution: `namei()`, component walking, symlink expansion, mount crossing, `relookup()`, realpath component tracking, and integration with pledge/unveil checks.

Entry setup:
- `ndinitat()` initializes `struct nameidata` for path operations relative to a directory fd.
- `component_push()` and `component_pop()` maintain `REALPATH` reconstruction state in `cn_rpbuf`.
- `namei()` allocates/copies the path from user or kernel space, rejects empty paths, optionally strips trailing slashes, sets the effective root, and runs pledge/unveil prechecks unless `KERNELPATH` is set.
- Starting vnode selection handles absolute paths, `AT_FDCWD`, and explicit directory fd lookups.
- Absolute `REALPATH` lookups initialize the reconstructed path with `/`.

Main namei loop:
- `namei()` calls `vfs_lookup()` repeatedly until the path resolves or a symlink must be followed.
- On final non-symlink success it runs `unveil_check_final()`, releases or preserves the namei buffer according to `SAVENAME`/`SAVESTART`, and returns.
- Symlink handling enforces `SYMLOOP_MAX`, reads link contents with `VOP_READLINK()`, splices remaining path text, restarts from root for absolute links, and updates realpath state.
- `BPU_LOCALTIME` and `BPU_ZONEINFO` impose stricter symlink/path rules for `/etc/localtime` and `/usr/share/zoneinfo`.

Component lookup:
- `vfs_lookup()` locks the starting directory, strips leading slashes, parses each component, sets `REQUIREDIR`, `ISLASTCN`, `MAKEENTRY`, and `ISDOTDOT`, and updates `ni_next`/`ni_pathlen`.
- It prevents `..` from escaping `ni_rootdir` or `rootvnode`.
- For `..` at mounted filesystem roots, it climbs to `mnt_vnodecovered` unless `NOCROSSMOUNT` is set.
- It calls `unveil_check_component()` before filesystem lookup.
- `VOP_LOOKUP()` failures with `EJUSTRETURN` are used for create-like final components; read-only filesystems reject mutating operations unless the pledge unveil path permits the special case.
- Successful directory vnodes mounted over by another filesystem are crossed using `vfs_busy()` and `VFS_ROOT()`.
- Symlinks are returned to `namei()` for interpretation when `FOLLOW` or `REQUIREDIR` applies.
- Final checks enforce directory requirements, read-only restrictions for delete/rename, optional parent retention, and `LOCKLEAF`.

Relookup:
- `vfs_relookup()` reacquires a previously parsed final component under a supplied directory vnode.
- It rejects null and dot-dot names, calls `VOP_LOOKUP()`, handles create-style `EJUSTRETURN`, applies read-only checks, optionally preserves the start directory, and unlocks the leaf if `LOCKLEAF` is absent.

Risks and notes:
- Vnode reference and lock ownership across `ni_dvp`, `ni_vp`, symlinks, and mount crossings is delicate.
- Pledge/unveil integration can transform some access errors into `EJUSTRETURN` for unveil setup.
- `REALPATH` state is maintained incrementally and must be rolled back on relative symlinks and `..`.
- `cn_consume` lets filesystems consume additional path bytes, so path length and required-directory state must be adjusted carefully.
- Mount traversal depends on `vfs_busy()` protection while calling `VFS_ROOT()`.
