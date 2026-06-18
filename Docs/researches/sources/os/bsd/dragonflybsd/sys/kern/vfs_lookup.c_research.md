# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_lookup.c

## Summary
Contains legacy lookup support, mainly `relookup()`, for old API rename paths.

## Main Responsibilities
- Exposes `varsym_enable` sysctl for variant symlink handling used elsewhere.
- Implements `relookup()` for re-looking up a single pathname component under old VOP lookup semantics.

## Important Behavior
`relookup()` requires `CNP_LOCKPARENT` and `CNP_PDIRUNLOCK` on entry. It locks the directory vnode, rejects empty names and `..`, calls `VOP_OLD_LOOKUP()`, and handles `EJUSTRETURN` as a valid create-missing result unless the operation is read-only.

On success, the directory parent remains locked and the target vnode is locked if it exists. On error, it unlocks the parent if needed and releases any target vnode.

## Risks
This is intentionally old API support for narrow rename conditions. It panics on dot-dot lookups and relies on caller-provided component-name flags being exactly as expected.
