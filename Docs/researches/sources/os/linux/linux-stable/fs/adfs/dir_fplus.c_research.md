# File Research: sources/os/linux/linux-stable/fs/adfs/dir_fplus.c
- Purpose: Implements ADFS F+ large-directory operations.
- Main functions: `adfs_fplus_validate_header`, `adfs_fplus_validate_tail`, `adfs_fplus_checkbyte`, `adfs_fplus_read`, `adfs_fplus_getnext`, `adfs_fplus_iterate`, `adfs_fplus_update`, `adfs_fplus_commit`.
- Format handling: Supports variable-sized directory storage with a header, entry array, name area, and tail.
- Validation: Checks magic values, size/entry bounds, tail metadata, and check byte.
- Object conversion: Reads little-endian big directory entries into `object_info` and copies names from the directory name area.
- Integration: Exports `adfs_fplus_dir_ops` and is selected by mount code when the disc record indicates F+ directories.
- Risks: Size calculations guard against malformed directories; update logic must locate entries by indirect address.
