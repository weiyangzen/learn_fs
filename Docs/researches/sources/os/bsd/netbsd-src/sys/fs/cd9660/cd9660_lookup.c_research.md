# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_lookup.c

## Summary
Implements pathname component lookup for CD9660 directories.

## Main Responsibilities
- Check directory execute permission and read-only delete/rename constraints.
- Consult namecache before scanning.
- Require exclusive directory vnode lock when scanning.
- Support associated-file lookup using leading `=` outside RRIP mode.
- Reuse the last lookup offset for common sequential lookups, with a second pass from the beginning when needed.
- Read directory blocks and validate ISO directory record lengths and block boundaries.
- Compare ISO/Joliet names with `isofncmp()` or Rock Ridge names from `cd9660_rrip_getname()`.
- Compute inode numbers from directory records and retrieve vnodes through vcache.
- Cache positive and negative results.
- Provide `cd9660_blkatoff()` helper to read a directory block and return an offset pointer.

## Key Interfaces
- `cd9660_lookup(void *v)`.
- `cd9660_blkatoff(struct vnode *vp, off_t offset, char **res, struct buf **bpp)`.

## Risks
The scanner stops on illegal record lengths or records crossing block boundaries. RRIP case-insensitive matching is mount-option controlled. Directory offset reuse improves performance but requires two-pass fallback to avoid missed entries.
