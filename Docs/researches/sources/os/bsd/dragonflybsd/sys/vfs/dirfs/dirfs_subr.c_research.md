# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_subr.c

Read completely: 893 lines.

## Role

This file implements dirfs support routines for node allocation/freeing, vnode association, host-path construction, passive fd cache management, host stat synchronization, open/close helpers, permission derivation, attribute mutation, file-size changes, and debug output.

## Main Responsibilities

- Node naming and lifecycle:
  - `dirfs_node_setname()`
  - `dirfs_node_alloc()`
  - `dirfs_node_drop()`
  - `dirfs_node_free()`
- File/node allocation:
  - `dirfs_alloc_file()` creates a dirfs node for a host child, optionally opens it with `openat()`, stats it, allocates a vnode, and marks the vnode for inactive finalization.
  - `dirfs_alloc_vp()` maps a dirfs node to a vnode, initializes vnode type and VM backing for regular files, and handles vnode allocation races.
  - `dirfs_free_vp()` detaches the vnode and drops the node's vnode-held reference.
- Host metadata:
  - `dirfs_nodetype()` maps host `stat` mode to vnode type.
  - `dirfs_node_stat()` fills dirfs node metadata from `lstat()` or `fstatat()`.
- Host path/fd helpers:
  - `dirfs_node_absolute_path()`
  - `dirfs_node_absolute_path_plus()`
  - `dirfs_findfd()`
  - `dirfs_dropfd()`
- Permission/open helpers:
  - `dirfs_node_getperms()` computes effective read/write/execute flags for the vkernel uid/gid.
  - `dirfs_open_helper()` opens a host file or directory using an existing parent fd or a relative path from `dirfs_findfd()`.
  - `dirfs_close_helper()` currently avoids closing descriptors directly because buffer-cache buffers may still reference them.
- Attribute mutation helpers:
  - `dirfs_node_chtimes()`
  - `dirfs_node_chflags()`
  - `dirfs_node_chmod()`
  - `dirfs_node_chown()`
  - `dirfs_node_chsize()`
- Passive fd cache:
  - `dirfs_node_setpassive()` adds/removes nodes from the per-mount fd cache and enforces `dirfs_fd_limit`.
- Diagnostics:
  - `dirfs_flag2str()`
  - `debug()`

## Synchronization and Lifetime Model

- Each node has a lock and a manual reference count.
- `dirfs_alloc_vp()` retries around vnode reclaim/allocation races and keeps a node reference for the vnode association.
- Parent links hold references from children to parents.
- Passive fd cache membership holds an additional node reference.
- `dirfs_node_setpassive()` closes cached descriptors only when vnode/node refs, inactive state, dirty VM flags, and dirty buffer trees indicate it is safe.
- Root node descriptors are treated specially and are not closed by passive-cache eviction.

## Important Interactions

- Uses host syscalls/functions: `openat()`, `lstat()`, `fstatat()`, `lutimes()`, `lchflags()`, `lchmod()`, `lchown()`, `truncate()`, and `close()`.
- Uses VFS/VM helpers:
  - `getnewvnode()`
  - `vinitvmio()`
  - `nvtruncbuf()`
  - `nvextendbuf()`
  - `VOP_FSYNC()`
- Called throughout `dirfs_vnops.c` for lookups, create/mkdir/symlink, getattr/setattr, read/write strategy, and reclaim/inactive behavior.

## Research Notes

- The host timestamp nanosecond fields are populated as `st_time * 1000000000L`, which appears to convert seconds to nanoseconds rather than using native subsecond fields.
- `dirfs_close_helper()` has the close call disabled under `#if 0`, reflecting a deliberate choice to avoid closing fds while buffer-cache state may still need them.
- Path construction walks parent pointers back to the root and fails if the resulting path exceeds `MAXPATHLEN` or if an unlinked node no longer has a path.
- `dirfs_node_chsize()` updates buffer-cache state before truncating/extending the host file.
