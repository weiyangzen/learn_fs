# File Research: sources/os/linux/linux-stable/fs/smb/client/fscache.h

## Summary
Declares CIFS fscache coherency structures and provides compile-time-gated fscache helpers. When `CONFIG_CIFS_FSCACHE` is enabled, it exposes real cookie acquisition, invalidation, and coherency helpers; otherwise it supplies no-op stubs so the rest of the CIFS client can compile without fscache support.

## Main Responsibilities
- Define packed volume coherency data for CIFS share-level cache volumes.
- Define inode coherency data based on last write and last change timestamps.
- Declare fscache functions implemented in `fscache.c`.
- Fill inode coherency data from Linux inode ctime and mtime.
- Expose the netfs cookie stored in `CIFS_I(inode)->netfs`.
- Invalidate fscache cookies with updated coherency and inode size.
- Test whether fscache is enabled for a given inode.
- Provide no-op replacements when CIFS fscache support is disabled.

## Key Interfaces
- `struct cifs_fscache_volume_coherency_data` includes resource id, volume creation time, and volume serial number.
- `struct cifs_fscache_inode_coherency_data` includes mtime and ctime seconds/nanoseconds.
- `cifs_fscache_get_super_cookie()`, `cifs_fscache_release_super_cookie()`, `cifs_fscache_get_inode_cookie()`, `cifs_fscache_unuse_inode_cookie()`, and `cifs_fscache_release_inode_cookie()` are declared for enabled builds.
- `cifs_fscache_fill_coherency()` packages inode timestamps for fscache.
- `cifs_inode_cookie()` returns the netfs cache cookie.
- `cifs_invalidate_cache()` calls `fscache_invalidate()` with coherency, size, and invalidation flags.
- `cifs_fscache_enabled()` wraps `fscache_cookie_enabled()`.

## Important Behavior
The enabled and disabled branches preserve the same call surface. Callers such as `file.c` can request fscache use, unuse, invalidation, or enabled-state checks without `#ifdef` at each call site. In disabled builds, cache acquisition succeeds as a no-op and enabled-state checks always return false.

The coherency helper zeroes the structure before writing timestamp fields, which keeps future padding or unused fields deterministic for fscache comparisons.

## Dependencies And Invariants
The header depends on Linux swap and fscache headers plus CIFS global structures. The packed coherency structures are part of fscache key/coherency ABI inside the kernel client and should not be changed casually. `cifs_inode_cookie()` assumes CIFS embeds a `netfs_inode` in its inode info.

## Risks
The header currently repeats several enabled-build function prototypes, which is harmless but easy to let drift during edits. Any change to coherency structure contents must be coordinated with `fscache.c` and with cache invalidation expectations in file I/O paths. Disabled-build stubs must preserve side-effect expectations for callers.
