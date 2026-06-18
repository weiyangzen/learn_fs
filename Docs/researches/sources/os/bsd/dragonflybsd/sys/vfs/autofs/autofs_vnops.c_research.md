# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vnops.c

Read completely: 603 lines.

## Role

This file implements the vnode operations and in-memory node helpers for DragonFlyBSD autofs directories. Autofs exposes synthetic directories that can trigger automountd-driven mounts when looked up or read. It also manages the autofs node tree and maps each `autofs_node` to a directory vnode on demand.

## Main Responsibilities

- Detect whether an autofs vnode has been covered by a real filesystem root with `test_fs_root()` and `nlookup_fs_root()`.
- Trigger automount resolution through `autofs_trigger_vn()` when a directory or child lookup is not cached and the calling thread is not an automountd-descendant thread.
- Implement VOPs:
  - `autofs_access()` permits all access; autofs-specific creation control is handled in mkdir.
  - `autofs_getattr()` synthesizes directory attributes from the autofs node.
  - `autofs_nresolve()` resolves child names from the autofs red-black child tree, or triggers automount first.
  - `autofs_nmkdir()` lets only automountd-descendant threads create synthetic autofs directories.
  - `autofs_readdir()` emits `.`, `..`, and child directory entries, or forwards readdir to a mounted real filesystem if the trigger resolves to a non-autofs root.
  - `autofs_reclaim()` disconnects a vnode from its autofs node without freeing the node.
  - `autofs_mountctl()` currently delegates to `vop_stdmountctl()`.
  - `autofs_print()` emits node diagnostics.
- Provide node lifecycle helpers:
  - `autofs_node_new()`
  - `autofs_node_find()`
  - `autofs_node_delete()`
  - `autofs_node_vn()`
- Define `autofs_vnode_vops`, the vnode operation table used by autofs.

## Synchronization and Lifetime Model

- Mount/node tree operations use `amp->am_lock`; child lookup requires the mount lock, and node creation/deletion require it exclusively.
- Each node has `an_vnode_lock` to serialize `an_vnode` association changes.
- `autofs_node_vn()` retries around `vget()` races and uses `vhold()`/`vdrop()` to stabilize an existing vnode.
- `autofs_reclaim()` clears `anp->an_vnode` and `vp->v_data`; node memory is intentionally freed by `autofs_node_delete()`, not by reclaim.
- Triggering releases the namecache lock around automount activity, then relocks and may return `ESTALE` when a real filesystem was mounted over the autofs node.

## Important Interactions

- Calls into generic name lookup with `nlookup_init()`, `nlookup()`, and `nlookup_done()` to verify whether an automount succeeded.
- Calls autofs control-layer functions from `autofs.h`, including `autofs_trigger()`, `autofs_cached()`, `autofs_ignore_thread()`, `autofs_path()`, and `autofs_node_uncache()`.
- Uses the generic VFS directory writer `vop_write_dirent()`.
- Delegates to the mounted filesystem's `VOP_READDIR()` when a trigger resolves to a non-autofs root vnode.

## Research Notes

- The key correctness path is avoiding duplicate automount triggers. `autofs_trigger_vn()` explicitly rechecks for a mounted root before and after calling `autofs_trigger()`.
- `autofs_getattr()` contains a disabled FreeBSD-style mount-on-stat path because DragonFly's current trigger mechanism could hang in `nlookup_fs_root()`.
- Directory offsets are reclen-based and strict: seeking into the middle of a synthetic dirent returns `EINVAL`.
- Security is intentionally narrow: ordinary threads cannot mkdir synthetic autofs nodes, while automountd descendants can build the autofs tree.
