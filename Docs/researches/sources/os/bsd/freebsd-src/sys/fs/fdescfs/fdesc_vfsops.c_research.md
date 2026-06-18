# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vfsops.c

## Purpose
Implements VFS-level mount, unmount, root, and statfs operations for the synthetic `/dev/fd` filesystem.

## Main Elements
- `fdesc_cmount()` is a compatibility shim into `kernel_mount()`.
- `fdesc_mount()` rejects update/rootfs mounts, allocates `fdescmount`, parses `linrdlnk`, `rdlnk`, and `nodup` options, creates the root vnode, sets shared lookup flags, assigns fsid, and sets mounted-from to `fdescfs`.
- `fdesc_unmount()` marks forced unmount in private flags, flushes vnodes while preserving the root reference, clears mount data, and frees mount state.
- `fdesc_root()` returns a locked reference to the cached root vnode.
- `fdesc_statfs()` computes available descriptor slots from current process descriptor table, resource limits, and RACCT limits, then reports synthetic block/file counts.
- Registers `fdescfs` as synthetic and jail-visible.

## Dependencies And Integration
Works with `fdesc_allocvp()` from vnode ops, FreeBSD file descriptor tables, resource accounting, and VFS mount option parsing.

## Risk Notes
`statfs` is process-relative because `/dev/fd` reflects the calling process descriptor table. Forced unmount relies on the shared hash mutex to coordinate against vnode allocation.
