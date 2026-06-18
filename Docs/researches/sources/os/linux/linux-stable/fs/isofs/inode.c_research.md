# File Research: sources/os/linux/linux-stable/fs/isofs/inode.c

Main ISOFS implementation: mount option parsing, superblock setup, inode cache, block mapping, inode loading, and module registration.

Key areas:
- Inode cache: `init_inodecache()`, `isofs_alloc_inode()`, `isofs_free_inode()`, and `destroy_inodecache()`.
- Mount parsing: `isofs_parse_param()` handles Rock Ridge/Joliet toggles, hide/showassoc, cruft, charset, name mapping, sessions, superblock sector, uid/gid, modes, block size, and compression disablement.
- Superblock setup: `isofs_fill_super()` chooses session start, scans ISO/High Sierra/Joliet descriptors, enforces read-only mount, sets block sizes and time bounds, loads NLS for Joliet, selects Rock Ridge vs Joliet root policy, installs dentry ops, and creates the root dentry.
- Name hashing/comparison: ISO and Joliet modes can be case-sensitive or case-insensitive, with Microsoft-style trailing-dot trimming for Joliet.
- Block mapping: `isofs_get_blocks()` maps file logical blocks through first extent and Level 3 multi-extent sections, with a 100-section sanity limit.
- Read operations: normal files use mpage read/readahead and bmap; compressed files switch to `zisofs_aops`.
- Inode loading: `isofs_read_inode()` reads directory records, handles split records, sets default modes, timestamps, extent info, Level 3 size, Rock Ridge overrides, compression format, and final inode/file/address-space ops.
- Identity: `__isofs_iget()` uses block/offset with `iget5_locked()` rather than inode number lookup.
- Registration: `init_iso9660_fs()` initializes inode cache and zisofs, then registers `iso9660`; exit unregisters and cleans up.

Important behaviors:
- Rock Ridge is preferred over Joliet when both are valid unless disabled, but broken empty/corrupt primary roots can force Joliet fallback.
- High Sierra disables Rock Ridge.
- The filesystem is read-only; attempts to mount read-write fail.
- `s_maxbytes` is set to 8 TB for multi-extent files.
- `cruft` truncates bogus high file-size byte for broken media.
- `overriderockperm` lets mount fmode/dmode override Rock Ridge permissions.
