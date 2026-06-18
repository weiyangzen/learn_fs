# File Research: sources/teaching/minix/minix/fs/isofs/super.h

This header defines ISO9660 volume descriptor constants and primary volume descriptor structure.

Constants:
- Volume descriptor types: boot, primary, supplementary, partition, set terminator.
- `MAX_ATTEMPTS` for scanning volume descriptors.

`struct iso9660_vol_pri_desc`:
- Packed 2048-byte primary volume descriptor fields: IDs, volume sizes, logical block size, path table locations, root directory record, publisher/application fields, volume timestamps, and padding.
- Appends in-memory fields: `inode_root` and `i_count`.
- Defines global `v_pri`.

Role:
- Shared volume descriptor state for mount, reads, stats, directory parsing, and SUSP handling.
