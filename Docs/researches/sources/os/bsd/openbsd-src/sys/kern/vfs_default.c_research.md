# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_default.c

Read completely: 174 lines.

Provides generic vnode-operation defaults shared by filesystems and special vnode implementations.

Implemented defaults:
- `vop_generic_revoke()` handles `REVOKEALL`, first force-unmounting an associated mounted block device if needed, then eliminating aliased special-device vnodes and finally calling `vgonel()` on the target.
- It serializes alias teardown with `vnode_mtx`, `VXLOCK`, and `VXWANT`.
- `vop_generic_badop()` panics for impossible/unimplemented operations.
- `vop_generic_bmap()` maps logical block to itself, returns the same vnode, and reports zero run length.
- `vop_generic_bwrite()` delegates buffer writes to `bwrite()`.
- `vop_generic_abortop()` frees the namei pathname buffer when appropriate.
- `vop_generic_lookup()` always fails with `ENOTDIR`.

Risks and notes:
- Revoke behavior is special-device sensitive and may force unmounts through `dounmount()`.
- Alias cleanup assumes `VALIASED` and special-device hash-chain invariants are intact.
- `vop_generic_abortop()` depends on precise `HASBUF` and `SAVESTART` flag ownership of `cn_pnbuf`.
- `vop_generic_badop()` is intentionally fatal, so operation vectors must only use it for unreachable methods.
