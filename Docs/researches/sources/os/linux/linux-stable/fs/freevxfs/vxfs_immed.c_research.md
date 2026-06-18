# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_immed.c

This file implements address-space reads for VxFS immediate-data inodes, whose file contents are stored directly inside the inode body.

Major responsibilities:
- Provide `vxfs_immed_read_folio()` to copy bytes from `vii_immed.vi_immed` into the requested folio.
- Mark the folio uptodate and unlock it after copying.
- Publish `vxfs_immed_aops` for immediate files, directories, and immediate symlinks where applicable.

Important design points:
- The read path does not perform block mapping; it reads from the in-core inode's immediate data buffer.
- The implementation iterates over all pages in the folio and copies a page at a time from the immediate area.
- Immediate symlinks may bypass this address-space operation and use `simple_symlink_inode_operations` with `i_link` pointing directly into the immediate buffer.

Key invariants:
- The folio is locked on entry and unlocked before return.
- Immediate data size is bounded by the inode immediate area declared in `vxfs_inode.h`.
- This is read-only support; no dirty/writeback path is provided.

External interfaces:
- Defines `vxfs_immed_aops`, referenced by `vxfs_iget()`.
