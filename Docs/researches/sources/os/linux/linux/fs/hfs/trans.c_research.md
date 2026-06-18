# File Research: sources/os/linux/linux/fs/hfs/trans.c

Purpose: Converts classic HFS Pascal-style Mac names to Linux names and Linux names back to Mac on-disk names, with optional NLS translation.

Key functions:
- `hfs_mac2asc()` converts `struct hfs_name` to an output byte string, maps `/` to `:`, and optionally translates disk charset to I/O charset.
- `hfs_asc2mac()` converts a Linux `qstr` to an HFS name, maps `:` to `/`, optionally translates I/O charset to disk charset, truncates to `HFS_NAMELEN`, and zero-pads the on-disk name field.

Dependencies and integration:
- Used by catalog key/thread construction and directory enumeration.
- Depends on `HFS_SB(sb)->nls_disk` and `nls_io`.

Risk notes:
- Conversion failures substitute `?` except for output-space exhaustion.
- Returned names are not null-terminated; callers must use explicit lengths.
