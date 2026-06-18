# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_immed.c

Read status: complete, 53 lines.

Purpose: provides address-space operations for VxFS immediate-data inodes, whose file data is stored inside the inode body.

Key flow:
- `vxfs_immed_read_folio()` locates inline data from `VXFS_INO(folio->mapping->host)->vii_immed.vi_immed + folio_pos(folio)`.
- Copies one or more pages into the folio, marks the folio uptodate, and unlocks it.
- `vxfs_immed_aops` exposes only `.read_folio`.

Risk note: correctness relies on VFS/file-size constraints preventing reads beyond the inline immediate data area; the routine itself does not clamp copy length to inode size or `VXFS_NIMMED`.
