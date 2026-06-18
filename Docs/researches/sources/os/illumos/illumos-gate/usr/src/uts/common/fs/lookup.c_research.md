# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lookup.c

## Role

Implements central illumos pathname lookup and vnode-to-path reverse lookup helpers. This file is VFS infrastructure rather than a specific filesystem.

## Major Responsibilities

- Converts user or kernel path strings into vnodes through `lookupname*()` and `lookuppn*()` APIs.
- Implements component-by-component pathname traversal in `lookuppnvp()`.
- Handles root/chroot/zone roots, `"."`, `".."`, mount crossing, symlinks, trailing slashes, and case-preserving lookup.
- Provides `traverse()` for crossing mounted-on vnodes to mounted filesystem roots.
- Implements reverse path discovery for `vnodetopath()` and `dogetcwd()`.
- Maintains and validates cached vnode paths (`v_path`) when enabled by `vfs_vnode_path`.

## Key Functions

- `lookupname()`: Convenience wrapper using current credentials.
- `lookupnameatcred()`: Copies a pathname from user/kernel space into a `pathname`, using a stack-sized buffer first and falling back to dynamic allocation for long paths.
- `lookupnameat()`: Lookup with a supplied start vnode and current credentials.
- `lookuppn()` / `lookuppnat()` / `lookuppnatcred()`: `pathname_t`-based wrappers.
- `lookuppnvp()`: Central path resolution engine.
- `traverse()`: Follows `v_vfsmountedhere` chains to mounted filesystem roots with VFS read locks.
- `vn_under()`: For reverse lookup, descends from a mounted filesystem root to the vnode covered by the mount.
- `vnode_match()`: Compares vnodes by special device clone semantics or real attributes.
- `dirfindvp()`: Scans a parent directory to find the name corresponding to a target vnode.
- `localpath()`: Converts a global resolved path into the portion visible below a current root.
- `vnode_valid_pn()`: Validates that a cached path still resolves to the expected vnode.
- `dirtopath()`: Reconstructs an absolute path to a directory by repeatedly looking up `".."` and scanning parents.
- `vnodetopath_common()`: Shared implementation for `vnodetopath()` and `dogetcwd()`.
- `vnodetopath()`: Public vnode-to-path helper.
- `dogetcwd()`: Implements current working directory resolution and caches process cwd strings.

## Path Lookup Semantics

`lookuppnvp()` performs the main namei loop:

- Requires an initial held vnode and optionally a held non-global root vnode.
- Rejects empty paths with `ENOENT`.
- Skips leading slashes in higher-level wrappers.
- Strips trailing slashes with `pn_fixslash()`, forcing final symlink following and final-directory validation.
- Handles `".."` specially at process root, zone root, and filesystem root.
- Crosses out of mounted filesystems by following `vfs_vnodecovered`.
- Uses `VOP_LOOKUP()` for each component.
- Retries lookup with `zone_kcred()` for mountpoint-crossing `".."` cases that fail with `EACCES`.
- Calls `traverse()` after successful lookup if the result has a mounted filesystem on it.
- Expands symlinks into the remaining pathname and enforces `MAXSYMLINKS`.
- Builds resolved path output in `rpnp` if requested.
- Returns parent vnode in `dirvpp` and/or final vnode in `compvpp`.

## Reverse Lookup Semantics

The reverse path logic prioritizes cached `v_path` but validates it before use:

- `vnode_valid_pn()` forward-lookups the cached path and compares the result with the expected vnode.
- For zone/chroot roots, it may resolve globally with `kcred` and then derive a local path.
- Stale cached paths are cleared through `vn_clearpath()`.
- `dirtopath()` reconstructs directory paths by walking to parents and scanning directory entries with `dirfindvp()`.
- Successfully reconstructed intermediate names are fed back through `vn_setpath()` so later lookups can use cache.
- `dogetcwd()` also maintains a process-level `u_cwd` refstr cache, validating it before returning.

## Edge Cases and Semantics

- Root escape is prevented by treating `".."` at `rootvp` or zone root as `"."`.
- Forced-unmounted filesystem roots return `EIO` when crossing covered vnode state is invalid.
- `ESTALE` at lookup roots, mounted roots, or the start vnode is translated to `ENOENT`.
- Trailing slash means final component must be a directory and symlinks must be followed.
- Case-insensitive lookup can return case-preserved names in resolved paths.
- `LOOKUP_CHECKREAD` is private to getcwd-style behavior and requires read permission on each directory, matching historical/standards expectations.
- `dirfindvp()` tolerates entries that disappear after `readdir()` by ignoring `ENOENT`.
- `dirfindvp()` has a special `.zfs` fallback because some ZFS pseudo-directories may not appear normally.

## Dependencies

Uses pathname helpers, vnode/VFS operations, mount traversal locks, zone state, auditing hooks, DNLC-related vnode path cache APIs, proc/user current directory/root fields, specfs clone helpers, and generic directory entry structures.
