# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_nlookup.c

## Summary
Implements DragonFlyBSD’s newer namecache-based pathname lookup API. It resolves paths into `nchandle` objects rather than old-style parent/leaf vnode lock combinations, improving parallelism and simplifying filesystem lookup contracts.

## Main Responsibilities
- Initializes and cleans up `nlookupdata` for normal, `*at`, raw, and early-root contexts.
- Performs full pathname resolution in `nlookup()`.
- Handles `.`, `..`, jail/root boundaries, mount crossings, symlink expansion, and generation-number retries.
- Provides mount glue lookup via `nlookup_mp()`.
- Reads symlink contents with `nreadsymlink()`.
- Checks pathname and target access through `naccess()` and `naccess_lva()`.
- Registers long-term nlookup statistics collection.

## Important Behavior
Intermediate path components require execute/search permission. Last components can request create, delete, rename, open, truncate, exclusive-create, parent-dvp reference, shared locks, no-cross-mount behavior, and other semantics via `NLC_*` flags.

Lookup uses namecache locks rather than directory vnode locks. Intermediate elements are optimized with shared or unlocked cache operations when possible; unresolved entries are locked and resolved. Symlinks allocate a path buffer, concatenate remaining path text, and restart lookup. Mount crossings resolve mount root namecache glue with `VFS_ROOT()` under `vfs_busy()`.

`naccess()` can short-circuit world-searchable directories using `NCF_WXOK`, refresh namecache permission/cache-control flags from `VOP_GETATTR_LITE()`, enforce read-only mount write restrictions, and feed final checks to `naccess_lva()`.

## Risks
The code is intentionally complex and generation-sensitive; many branches retry when namecache generations change or parent directories disappear. There are diagnostic comments around broken chroot/jail traversal, autofs/NFS retry behavior, stale entries, and lock cycling. Access decisions depend on cached namecache flags being refreshed correctly.
