# File Research: sources/os/linux/linux/fs/exfat/exfat_raw.h

## Purpose
Defines exFAT on-disk constants and packed structures used to interpret boot sectors and directory entries.

## Main Contents
- Signatures and identifiers: boot signatures, `"EXFAT   "` filesystem name.
- Cluster sentinels: free, EOF, bad, reserved/first cluster, maximum cluster count.
- Allocation flags: `ALLOC_POSSIBLE`, `ALLOC_FAT_CHAIN`, `ALLOC_NO_FAT_CHAIN`.
- Dentry type byte values: unused, deleted, bitmap, upcase, volume, file, stream, name, ACL/vendor entries.
- File attributes: readonly, hidden, system, volume, subdir, archive.
- On-disk sizes: 32-byte dentries, 15 UTF-16 code units per filename dentry, 11-code-unit volume labels.
- Packed structs: `boot_sector` and union-based `exfat_dentry`.
- Timestamp bounds and timezone-valid bit.

## Integration Role
All parser and writer code in `dir.c`, `super.c`, `fatent.c`, `balloc.c`, `inode.c`, and `nls.c` relies on these exact packed layouts and constants to avoid ABI drift from the exFAT disk format.

## Notable Invariants And Risks
- The union in `struct exfat_dentry` overlays many entry forms on one 32-byte record.
- Endianness conversion is required for all multibyte on-disk fields.
- Incorrect changes here would corrupt disk-format interpretation globally.
