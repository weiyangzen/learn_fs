# File Research: sources/os/linux/linux-stable/fs/adfs/dir_f.c
- Purpose: Implements classic ADFS F-format directory operations.
- Main functions: `adfs_f_validate`, `adfs_f_read`, `adfs_f_setpos`, `adfs_f_getnext`, `adfs_f_iterate`, `adfs_f_update`, `adfs_f_commit`.
- Format handling: Reads/writes packed little multi-byte fields with helper functions and uses fixed-size directory entries.
- Validation: Checks directory start/end metadata and directory check bytes.
- Object conversion: Converts between `adfs_direntry` and generic `object_info`.
- Integration: Exports `adfs_f_dir_ops` for use by common directory and mount code.
- Risks: Fixed name length and check-byte recomputation make boundary and corruption handling important.
