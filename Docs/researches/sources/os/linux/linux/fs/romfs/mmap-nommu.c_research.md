# File Research: sources/os/linux/linux/fs/romfs/mmap-nommu.c

## Purpose
Provides NOMMU direct-mapping support for ROMFS files stored on MTD devices.

## Main Responsibilities
- Determine whether a ROMFS file mapping can be directly mapped through the underlying MTD device.
- Validate mapping offsets and lengths against file size and MTD size.
- Expose file operations that support NOMMU mapping capabilities.

## Important Control Flow
- `romfs_get_unmapped_area()`:
  - Requires an MTD-backed superblock.
  - Rejects mappings beyond EOF, nonzero requested addresses, offsets beyond MTD size, and ranges outside the MTD.
  - Adds the ROMFS inode data offset to the file offset.
  - Delegates to `mtd_get_unmapped_area()`.
  - Translates `-EOPNOTSUPP` to `-ENOSYS`.
- `romfs_mmap_prepare()`:
  - Allows only NOMMU shared mappings.
  - Rejects private/copy mappings with `-ENOSYS`.
- `romfs_mmap_capabilities()`:
  - Returns `NOMMU_MAP_COPY` without MTD.
  - Otherwise delegates to `mtd_mmap_capabilities()`.

## Exported Object
- `const struct file_operations romfs_ro_fops`
  - Read-only file operations with llseek, read_iter, splice_read, mmap_prepare, get_unmapped_area, and mmap_capabilities.

## Dependencies and Integration
- Compiled only on NOMMU MTD ROMFS builds.
- Uses `ROMFS_I(inode)->i_dataoffset` from `internal.h`.
- Used by ROMFS regular files through `romfs_ro_fops`.

## Research Notes
The file is intentionally limited to direct mappings that the MTD layer can support safely. It prevents mappings outside the ROMFS file or backing MTD range.
