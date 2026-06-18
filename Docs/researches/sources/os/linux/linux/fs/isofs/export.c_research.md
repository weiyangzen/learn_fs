# File Research: sources/os/linux/linux/fs/isofs/export.c

Implements NFS export support for ISOFS, which cannot use default iget-based helpers because ISOFS uses `iget5_locked()` with block/offset identity.

Key functions:
- `isofs_export_iget()` validates block range, gets an inode by block/offset, checks generation, and returns an alias dentry or `-ESTALE`.
- `isofs_export_get_parent()` finds a directory parent by reading the normalized child directory’s `..` entry, normalizing its block/offset, and returning that inode.
- `isofs_export_encode_fh()` encodes block, offset, generation, and optionally parent block/offset/generation. It supports compact NFSv2-sized handles by packing offsets into 16-bit fields.
- `isofs_fh_to_dentry()` and `isofs_fh_to_parent()` decode file handles back to dentries.

Exports `isofs_export_ops` with encode, decode, parent decode, and get_parent hooks.
