# File Research: sources/os/linux/linux-stable/fs/coda/symlink.c

This file implements Coda symlink page filling through a Venus `readlink` upcall.

Key responsibilities:
- Defines `coda_symlink_filler()` as the address-space `read_folio` handler for symlinks.
- Defines `coda_symlink_aops`.

Important control flow:
- Retrieves the owning inode from `folio->mapping->host`.
- Extracts the Coda fid from `struct coda_inode_info`.
- Calls `venus_readlink()` into the folio page buffer with a maximum length of `PAGE_SIZE`.
- Completes the folio read with success based on the Venus call result.

Dependencies:
- Depends on `venus_readlink()` from `upcall.c`.
- Used by Coda inode creation paths for symlink inodes.

Risks and invariants:
- The symlink target is fetched lazily from Venus into the page cache.
- Venus must NUL-terminate or otherwise respect the length protocol enforced by `venus_readlink()`.
