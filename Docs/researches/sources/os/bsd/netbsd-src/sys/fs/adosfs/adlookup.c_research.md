# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adlookup.c

## Summary
Implements ADOSFS vnode lookup over AmigaDOS directory hash chains.

## Main Responsibilities
- Check directory execute permission and read-only constraints for delete/rename.
- Use NetBSD namecache before scanning.
- Handle synthetic `.` and `..` lookups, including unlocking parent for dot-dot vget.
- Hash the requested component using AmigaDOS hashing and scan the selected hash chain.
- Compare names case-insensitively unless `ADOSFS_EXACTMATCH` is enabled.
- Return `EJUSTRETURN` for last-component create/rename misses on writable directories.
- Cache positive and negative lookup results when appropriate.

## Key Interfaces
- `adosfs_lookup(void *v)` vnode operation.

## Risks
Directory traversal depends on on-disk hash-chain integrity. The code tracks chain lengths in `tabi` as an optimization; corrupt chains can cause repeated vget/read failures. Dot-dot lookup intentionally unlocks the parent to avoid deadlock.
