# File Research: sources/os/linux/linux-stable/fs/erofs/ishare.c

## Summary
Implements experimental EROFS page-cache sharing among files with identical content fingerprints.

## Main Responsibilities
- Builds shared anonymous inodes keyed by xattr fingerprints.
- Links real inodes to shared inodes.
- Routes reads and mmap through backing files using shared mappings.
- Rejects direct I/O for shared files.
- Initializes and tears down the anonymous share mount.

## Key APIs
- `erofs_ishare_fill_inode()`
- `erofs_ishare_free_inode()`
- `erofs_real_inode()`
- `erofs_ishare_fops`

## Important Behavior
Fingerprint lookup uses `xxh32()` as the iget hash and full fingerprint comparison for equality. Reads clone the caller `kiocb` onto an allocated backing file whose inode and mapping point at the shared inode.

## Risks
Correctness depends on fingerprint uniqueness and matching aops/file size. The shared inode keeps a list of real inodes, and `erofs_real_inode()` grabs any live one for actual mapping context.
