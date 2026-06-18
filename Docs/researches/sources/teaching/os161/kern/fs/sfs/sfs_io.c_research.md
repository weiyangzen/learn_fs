# File Research: sources/teaching/os161/kern/fs/sfs/sfs_io.c

Provides SFS block I/O, file I/O, and metadata I/O plumbing.

Block I/O:
- `sfs_rwblock` calls `DEVOP_IO`, panics on `EINVAL`, retries `EIO` up to 10 times, and logs retry/give-up messages.
- `sfs_readblock` and `sfs_writeblock` initialize kernel `uio` objects with `SFSUIO` and require full-block length.

File I/O:
- `sfs_partialio` handles sub-block reads/writes by reading the whole disk block or zero-filling sparse reads, applying `uiomove`, and writing back on writes.
- `sfs_blockio` handles full-block I/O directly through `uio`, temporarily translating file offsets/resid to device offsets/resid.
- `sfs_io` trims reads at EOF, processes leading partial block, whole blocks, trailing partial block, updates file size on writes, and restores unread EOF residue.

Metadata I/O:
- `sfs_metaio` handles small kernel-resident metadata records that do not cross block boundaries. It maps the containing block, reads it, copies selected bytes in or out, writes back on metadata writes, and grows vnode size if needed.

Notable constraints:
- Uses static buffers for partial and metadata I/O, requiring the VFS biglock.
- Sparse reads return zeros for unmapped blocks.
