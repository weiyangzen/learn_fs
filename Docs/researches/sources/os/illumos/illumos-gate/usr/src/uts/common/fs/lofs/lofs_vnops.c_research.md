# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vnops.c

## Role

Implements LOFS vnode operations. Most operations unwrap the LOFS vnode to its real vnode and delegate, while lookup, create, link, rename, realvp, and inactive contain the core stacking semantics.

## Major Responsibilities

- Presents a full vnode operation table for LOFS shadow vnodes.
- Delegates ordinary file operations to underlying vnodes.
- Wraps newly discovered underlying vnodes in LOFS lnodes.
- Maintains correct behavior across nested LOFS mounts, autofs, mount loops, and special device vnodes.
- Enforces readonly semantics for operations where generic code might only check one side of a stacked operation.
- Frees lnodes through `lo_inactive()`.

## Key Functions

- `lo_open()`: Opens the real vnode. If the underlying VOP substitutes a different vnode, wraps it in a new lnode, propagates loop flags for directories, handles device `specvp()`, and releases the old LOFS vnode.
- `lo_close()`, `lo_read()`, `lo_write()`, `lo_ioctl()`, `lo_setfl()`, `lo_getattr()`, `lo_setattr()`, `lo_fsync()`: Pass through to the real vnode.
- `lo_access()`: Rejects writes to regular files on readonly LOFS mounts before delegating.
- `lo_inactive()`: Calls `freelonode()` for lnode cleanup.
- `lo_lookup()`: Central path lookup logic with dot/dotdot handling, subordinate mount traversal, loop detection, autofs loop termination, and wrapping of returned vnodes.
- `lo_create()`: Delegates create and wraps result. Special-cases single regular-file LOFS roots where some underlying filesystems return `ENOSYS` for create-on-root.
- `lo_link()`: Resolves lofs and realvp layers on source/target, rejects source readonly, and enforces same real VFS.
- `lo_rename()`: Rejects readonly source LOFS, protects mounted-on directories hidden by LOFS layers, and recurses through stacked LOFS layers as needed.
- `lo_mkdir()`, `lo_rmdir()`, `lo_symlink()`, `lo_readlink()`, `lo_readdir()`: Mostly pass-through with wrapping where needed.
- `lo_realvp()`: Unwraps all LOFS layers and asks lower filesystems for their real vnode if available.
- `lo_cmp()`: Compares real underlying vnodes.
- VM and page operations (`lo_getpage`, `lo_putpage`, `lo_map`, `lo_addmap`, `lo_delmap`, `lo_pageio`, `lo_dispose`) delegate to the real vnode.

## Lookup and Loop Handling

`lo_lookup()` is the most complex function. It handles:

- Empty component as `"."` unless xattr lookup/create flags require underlying lookup.
- `".."` crossing out of real mounted filesystems.
- Returning `dvp` for `"."` to avoid stale file handles.
- `LO_NOSUB` to suppress traversal into subordinate mounts.
- Device-special wrapping via `specvp()`.
- Direct loops where lookup returns the current LOFS root.
- Indirect loops through multiple LOFS layers.
- Autofs/LOFS loops where returning the covered vnode once is insufficient; `LO_AUTOLOOP` forces directory children to resolve to covered vnodes to terminate traversal.
- Forced lnode creation with `LOF_FORCE` for loop-termination identities.

## Edge Cases and Semantics

- `lo_access()` protects readonly LOFS regular files independently of underlying filesystem writability.
- `lo_link()` prevents hard-linking from a readonly LOFS source into a writable LOFS target over the same real filesystem.
- `lo_rename()` prevents renames from readonly LOFS mounts even if the underlying filesystem is writable.
- `lo_rename()` checks hidden mountpoints when target directory is not itself a LOFS vnode.
- `lo_create()` handles a single regular file mounted as the LOFS root as an existing-file create/truncate operation.
- `lo_dispose()` avoids calling dispose on `VN_ISKAS()` vnodes.
- Security attribute setting checks LOFS readonly state before delegation.

## Operation Table

`lo_vnodeops_template` registers broad vnode coverage: open, close, read/write, ioctl, getattr/setattr, access, lookup/create/remove/link/rename, directory ops, symlink ops, locking, space, realvp, page/mmap operations, poll, dump, pathconf, dispose, security attributes, and share locks.

## Dependencies

Depends on `lofs_subr.c` for `makelonode()`, `realvp()`, `vtoli()`, `vtol()`, and `freelonode()`. Interacts heavily with generic VFS lookup/traversal, specfs, autofs behavior, vnode readonly checks, and lower filesystem vnode operations.
