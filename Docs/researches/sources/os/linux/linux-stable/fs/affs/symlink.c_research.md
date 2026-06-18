# File Research: sources/os/linux/linux-stable/fs/affs/symlink.c

This file implements AFFS symlink page-cache population and symlink inode operations.

Major responsibilities:
- Reads a symlink inode’s AFFS header block.
- Converts AFFS symlink syntax into a Linux path string in the target folio.
- Handles Amiga assign or volume-name prefixes containing `:`.
- Converts doubled slash patterns into parent-directory `..` components.
- Provides address-space operations and inode operations for symlink inodes.

Conversion details:
- If the stored symlink contains `:`, the code prepends the mount’s configured `s_prefix` or `/`, then copies the volume/assign name up to `:`, emits `/`, and continues after the colon.
- The symlink prefix and volume fields are protected by `symlink_lock`.
- Output is capped at 1023 bytes plus NUL.
- `page_get_link` is used as the VFS `.get_link` implementation after the folio is filled.

Error handling:
- Failure to read the symlink header block unlocks the folio and returns `-EIO`.
- Successful reads mark the folio uptodate before unlocking.
