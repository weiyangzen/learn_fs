# File Research: sources/teaching/minix/minix/fs/isofs/super.c

This file reads ISO9660 volume descriptors and initializes the root inode.

Key functions:
- `release_vol_pri_desc(vol_pri)`: releases the root inode reference held by the primary volume descriptor.
- Internal `create_vol_pri_desc(vol_pri, buf)`: copies and validates primary volume descriptor, sets LMFS block size/usage, parses root directory record, and stores root inode.
- `read_vds(vol_pri, dev)`: scans volume descriptors starting at byte 32768 until set terminator or max attempts.

Validation:
- Requires standard ID `CD001`, descriptor version 1, and logical block size >= 2048.
- Requires both a primary descriptor and a set terminator.

Root handling:
- Builds a one-extent view from root directory record.
- Calls `read_inode()` to create/cache root inode.
- Sets root inode `i_count = 1` and stores it in `v_pri`.

Role:
- Equivalent of superblock load for read-only ISO9660.
