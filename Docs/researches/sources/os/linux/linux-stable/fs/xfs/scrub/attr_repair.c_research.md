# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/attr_repair.c

## Purpose
Repairs an inode’s extended attributes by salvaging valid-looking xattrs from damaged metadata, replaying them into a temporary file, and atomically exchanging the rebuilt attr fork into the target inode. It also handles live parent-pointer updates during repair.

## Main Entry Points
- `xrep_setup_xattr`: creates a temporary regular file and enables directory-entry gates when parent pointers exist.
- `xrep_xattr`: top-level repair.
- `xrep_xattr_reset_fork`: clears the target inode attr fork.
- `xrep_xattr_reset_tempfile_fork`: clears the tempfile attr fork after exchange.
- `xrep_xattr_swap`: exchanges or copies rebuilt attr fork contents.

## Key Behavior
Salvage stores attr records in `xfarray` and names/values in `xfblob`. Shortform entries, leaf local entries, and leaf remote entries have separate recovery paths. Remote values are retrieved with attr remote helpers, and corrupt remote values are quietly dropped if they fail checksum/corruption checks.

For non-inline attr forks, repair scans mapped attr fork extents and searches the buffer cache for possible leaf blocks. Because remote attr buffers can be multiblock and alias-prone, `xrep_xattr_find_buf` first looks for existing buffers in the range and otherwise reads one block with `XBF_TRYLOCK`; temporary single-block reads without buffer ops are staled before release.

To constrain memory, salvaged attrs are periodically flushed into the tempfile. Flushing commits the scrub transaction, drops ILOCKs, locks the tempfile with normal xattr IOLOCK semantics, inserts stashed attrs with `xfs_attr_set`, clears staging arrays, recreates the scrub transaction, and relocks the target.

Parent-pointer filesystems add a live dirent hook. While attr repair is flushing or exchanging, dirent updates pointing to the target inode are stashed as parent add/remove records and later replayed against the tempfile. If parent-pointer conflicts occur during a flush, repair can fully reset the tempfile and restart salvage with flushing disabled.

Final rebuild either removes the attr fork if no attrs were salvaged or finalizes the tempfile, replays all parent-pointer updates, prepares local forks for mapping exchange, exchanges attr fork mappings, reaps old attr fork blocks now attached to the tempfile, rolls transactions, unlocks the tempfile, and invalidates cached ACLs.

## Dependencies and Interactions
Requires rmapbt to reap old attr fork blocks and exchange-range support for atomic fork replacement. Uses tempfile, tempexch, xfile/xfarray/xfblob, attr, parent pointer, ACL, bmap, reap, and directory hook infrastructure.

## Failure Handling
Repair returns unsupported without rmapbt or exchange-range. Parent-pointer live update allocation failure marks repair aborted and causes `-EIO`. Staging allocations are torn down in all exit paths. If both original and tempfile attr forks are local and fit, repair avoids mapping exchange by copying local attr data directly.
