# File Research: sources/os/linux/linux-stable/fs/isofs/export.c

Provides NFS export operations for ISOFS, which cannot use default inode-number based helpers because ISOFS uses `iget5_locked()` with block/offset identity.

Key paths:
- `isofs_export_encode_fh()` encodes inode block, offset, generation, and optionally parent block/offset/generation into file handles.
- `isofs_fh_to_dentry()` and `isofs_fh_to_parent()` decode handles and call `isofs_export_iget()`.
- `isofs_export_iget()` validates block range, loads the inode with `isofs_iget()`, checks generation, and returns an alias dentry.
- `isofs_export_get_parent()` reads the child directory's `..` entry, normalizes its block/offset, and obtains the parent inode alias.

Important invariants:
- Directory inode identities are normalized to the `.` entry, so parent lookup can find `..` in the same directory block.
- NFSv2 handle length limitations pack child and parent offsets into 16-bit fields.
- Generation mismatches return `-ESTALE`.
