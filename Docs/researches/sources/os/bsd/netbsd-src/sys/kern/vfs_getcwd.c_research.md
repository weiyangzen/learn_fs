# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_getcwd.c

## Purpose
Implements current-directory path reconstruction and ancestry checks by walking from a vnode up toward a root, using the name cache when possible and directory scanning as fallback.

## Main Interfaces
- `getcwd_scandir`: find a vnode's parent and optional name by looking up `..` and scanning the parent directory.
- `getcwd_common`: shared upward traversal used by `getcwd`, ancestry checks, and vnode path reconstruction.
- `vn_isunder`: tests whether one directory lies under another root.
- `proc_isunder`: tests whether one process root is equal to or under another process root.
- `sys___getcwd`: syscall implementation that builds a path backward into a kernel buffer and copies it out.
- `vnode_to_path`: best-effort path reconstruction for an arbitrary referenced vnode using reverse namecache plus `getcwd_common`.

## State And Control Flow
Paths are built backward from the end of a buffer. `getcwd_common` references both starting vnode and root, handles crossing covered mount roots, optionally checks execute/read access, tries `cache_revlookup`, and falls back to `getcwd_scandir` on cache miss. Directory scanning locks the lower vnode, looks up `..`, locks the parent, reads directory blocks with `VOP_READDIR`, and matches entries by file id.

## Dependencies And Integration
Uses cwdinfo, vnode references/locks, VOP_LOOKUP, VOP_GETATTR, VOP_ACCESS, VOP_READDIR, namecache reverse lookup, mount topology, credentials, directory entry format, UIO setup, and emulation path stripping.

## Risks And Edge Cases
- Path reconstruction is inherently race-prone because vnode-to-parent mappings are not authoritative.
- Directory scanning matches by file id and does not verify by lookup that the found name resolves back to the child.
- Malformed directory records return `EINVAL`; comments note possible infinite retry behavior for pathological NFS/directory cases.
- Union mount fallback code is disabled.
- Buffer exhaustion returns `ERANGE`, and traversal is bounded by a vnode-count limit derived from output length.

## Filesystem Relevance
High. This is VFS reverse-path logic used for `getcwd`, chroot/ancestry checks, procfs-style visibility, and best-effort vnode path reporting.
