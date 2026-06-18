# File Research: sources/os/linux/linux/fs/affs/symlink.c

Purpose: implements AFFS symlink page loading and symlink inode operations.

Key interfaces:
- `affs_symlink_aops.read_folio = affs_symlink_read_folio`.
- `affs_symlink_inode_operations`: `get_link = page_get_link`, `setattr = affs_setattr`.

Implementation notes:
- Reads the symlink text from the inode’s AFFS header block.
- If the stored name contains `:`, treats the prefix as an AFFS assign/volume name and prepends mount `s_prefix` or `/`.
- Converts repeated slash semantics into Unix parent-directory references by inserting `..` when a slash follows a slash.
- Caps generated link text at 1023 bytes and NUL-terminates the folio buffer.
- Marks the folio uptodate and unlocks it on success.

Dependencies:
- Uses AFFS block read/release helpers and `symlink_lock` for stable prefix access.

Edge cases:
- Block read failure unlocks the folio and returns `-EIO`.
