# File Research: sources/os/linux/linux-stable/fs/exfat/exfat_raw.h

This header defines exFAT on-disk constants and packed raw structures.

Key elements:
- Defines boot signatures, filesystem name string, max filename length, volume flags, special cluster values, reserved cluster numbering, and maximum cluster count.
- Defines raw directory entry type bytes such as `EXFAT_FILE`, `EXFAT_STREAM`, `EXFAT_NAME`, `EXFAT_BITMAP`, `EXFAT_UPCASE`, and volume/vendor entries.
- Provides classification macros for critical/benign primary and secondary entries.
- Defines checksum modes `CS_DIR_ENTRY`, `CS_BOOT_SECTOR`, and `CS_DEFAULT`.
- Defines file attribute bits and writable mask `EXFAT_ATTR_RWMASK`.
- Defines boot sector layout in packed `struct boot_sector`.
- Defines packed `struct exfat_dentry` union covering file primary, stream extension, name, bitmap, upcase, volume label, vendor, and generic secondary entries.
- Defines timestamp range constants and timezone-valid flag.

Important dependencies:
- `dir.c`, `inode.c`, `namei.c`, `balloc.c`, `fatent.c`, and `nls.c` interpret and write these raw fields using little-endian conversions.
- `exfat_fs.h` builds internal helper types and logic on top of these raw constants.

Critical contracts:
- Directory entries are exactly 32 bytes.
- File names are stored as 15 UTF-16 code units per name secondary entry.
- Cluster 0 and 1 are reserved; data cluster numbering starts at 2.
- The stream extension contains allocation flags, valid size, start cluster, and logical size, which drives block mapping and writeback behavior.
