# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_extern.h

This header centralizes cross-file prototypes for the FreeVxFS driver.

Major responsibilities:
- Declare block mapping, fileset header, inode, lookup, Object Location Table, and shared page/buffer helper interfaces.
- Expose FreeVxFS address-space operations for normal and immediate-data files.
- Expose directory inode/file operations for VFS inode setup.
- Keep implementation files decoupled while avoiding broader header dependencies.

Important design points:
- The prototypes mirror the Makefile object split: bmap, fshead, inode, lookup, OLT, subroutines, and superblock code.
- Most functions are internal to the FreeVxFS driver even though declared with `extern`; they are not exported kernel symbols.
- The header distinguishes structural inode lookup (`vxfs_stiget`), block/extent based lookup (`vxfs_blkiget`), and ordinary inode lookup (`vxfs_iget`).

Key invariants:
- Callers must use the appropriate inode lookup path for the phase of mount: raw/block reads during superblock setup, pagecache-backed reads after inode lists are established.
- `vxfs_get_page()` results must be released with `vxfs_put_page()`.

External interfaces:
- Internal driver API only; no module exports are declared here.
