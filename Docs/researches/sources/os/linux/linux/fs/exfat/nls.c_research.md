# File Research: sources/os/linux/linux/fs/exfat/nls.c

## Purpose
Implements filename character conversion, case folding through the exFAT upcase table, name hashing support, and loading of on-disk or default upcase tables.

## Main Interfaces
- `exfat_toupper`
- `exfat_uniname_ncmp`
- `exfat_utf16_to_nls`
- `exfat_nls_to_utf16`
- `exfat_create_upcase_table`
- `exfat_free_upcase_table`

## Key Data Flow
The file includes the compressed recommended default upcase table and expands it into a 65,536-entry table. `exfat_create_upcase_table()` scans root directory entries for an upcase-table entry, loads it from disk, verifies its checksum, and falls back to the default table for non-I/O validation failures.

Name conversion has two modes. UTF-8 mode uses kernel UTF-8/UTF-16 helpers and computes name hashes from uppercased UTF-16 code units. Non-UTF-8 mode uses the mounted NLS table, converting between byte strings and UCS-2. Invalid half-width characters and control characters mark conversion as lossy; create paths reject lossy names while lookup can tolerate them for compatibility. UTF-16 surrogate pairs above U+FFFF are converted to replacement characters in NLS output because kernel NLS is UCS-2 oriented.

## Dependencies
Uses raw directory-entry types, checksum helpers, `exfat_get_dentry()`, FAT cluster traversal, buffer heads, kernel NLS, and UTF conversion APIs.

## Notable Invariants And Risks
- exFAT lookup is case-insensitive through the upcase table.
- Name hashes are computed over uppercased UTF-16 data.
- On-disk upcase table checksum mismatch causes fallback only for non-I/O errors.
