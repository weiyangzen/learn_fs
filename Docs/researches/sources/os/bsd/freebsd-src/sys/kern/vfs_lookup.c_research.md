# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_lookup.c

## Role

Implements FreeBSD pathname resolution: `namei()`, locked fallback lookup, capability-mode path restrictions, symlink expansion, mount crossing, union fallback, and relookup of final components for filesystem operations.

## Main Entry Points

- `namei()` is the public pathname-to-vnode resolver.
- `vfs_lookup()` performs the locked component-by-component lookup after fast path cache lookup aborts or partially completes.
- `vfs_relookup()` reacquires a final component from a parent directory after a caller has temporarily dropped locks.
- `vfs_lookup_nameidata()` recovers the enclosing `nameidata` from a component name when appropriate.
- `vfs_lookup_isroot()` tests whether `..` would cross a process, jail, chroot, or global root boundary.

## Initialization

`nameiinit()` creates the `NAMEI` UMA zone, registers a special `crossmp` vnode operation vector, allocates the `vp_crossmp` placeholder vnode, and marks it with `VIRF_CROSSMP`. The placeholder is used during mount traversal to represent a synthetic parent when crossing mount points.

## Namei Flow

`namei()` validates debug state and flags, copies in the pathname, records tracing/audit data, then first attempts `cache_fplookup()`. If the fast path handles the request, it returns directly. Otherwise it sets up a starting directory from an explicit start vnode, `AT_FDCWD`, fd-relative lookup, or root, then loops through `vfs_lookup()` and symlink expansion until a final vnode is returned or an error occurs.

Absolute symlinks preserve ABI root during the first pass and switch to native root only after a restarted lookup. Empty paths are handled specially only when `EMPTYPATH` is set.

## Locked Lookup Flow

`vfs_lookup()` trims trailing slashes, locks the starting directory, parses one component at a time, handles `.`/`..` special cases, checks MAC lookup policy, calls `VOP_LOOKUP()`, follows mount points through `vfs_lookup_cross_mount()`, handles symlink detection, enforces read-only restrictions for modifying operations, and returns parent/leaf locks according to `LOCKPARENT`, `WANTPARENT`, `LOCKLEAF`, and `LOCKSHARED`.

It supports `ERELOOKUP` by retrying the same component, `EJUSTRETURN` for create/rename cases where the leaf does not exist, and union mounts by retrying lookup on the covered vnode when a root vnode lookup misses.

## Capability And Boundary Enforcement

Capability mode and `RBENEATH` set strict-relative lookup state. The code rejects absolute lookups, `AT_FDCWD` in capability mode, disallowed `..`, and attempts to escape the starting directory. When dotdot traversal is permitted, `nameicap_tracker_add()` records mount rename locks so concurrent renames cannot move a traversed directory out from under the lookup.

`lookup_cap_dotdot` and `lookup_cap_dotdot_nonlocal` sysctls tune dotdot handling and non-local filesystem behavior. Ktrace capability violations are recorded through `NI_CAP_VIOLATION()`.

## Locking Details

The lookup path dynamically chooses shared or exclusive locks. `enforce_lkflags()` upgrades shared locks when a mount lacks `MNTK_LOOKUP_SHARED`; `needs_exclusive_leaf()` chooses exclusive leaf locking for operations that require it. Cross-mount traversal handles special `VV_CROSSLOCK` recursion rules and uses `vfs_busy()` around `VFS_ROOT()`.

## Dependencies

This is one of the central consumers of name cache, vnode locks, mount references, MAC checks, audit hooks, Capsicum state, prison roots, process working directories, and filesystem `VOP_LOOKUP` and `VOP_READLINK` methods.

## Notes

Most complexity comes from preserving legacy VFS lock contracts while supporting fast path lookup, capability restrictions, ABI roots, shared lookup locks, forced unmount races, and mount traversal.
