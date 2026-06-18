# File Research: sources/os/linux/linux/fs/ntfs/dir.h

## Purpose
Declares the NTFS directory lookup and empty-directory interfaces plus the small result structure used to report name aliasing information back to namei code.

## Key Elements
`struct ntfs_name` packages the matched MFT reference, NTFS file-name namespace type, UTF-16 name length, and optional little-endian UTF-16 name payload. `ntfs_lookup_inode_by_name()` uses it when a case-insensitive or DOS namespace match requires callers to handle dcache aliasing against the canonical long name. The header also exports the global `$I30` UTF-16 constant and `ntfs_check_empty_dir()`.

## Dependencies And Integration
Includes `inode.h` for `struct ntfs_inode` and related NTFS types. The declarations are consumed by NTFS name lookup, directory operation, inode sync, index, and xattr code that needs directory `$I30` access.

## Behavior/Risks
The `ntfs_name` flexible array is packed and allocated to exact name size by callers. Consumers must respect the documented ownership convention: lookup may allocate a result, may set `*res` to NULL for exact non-DOS matches, and uses `len == 0` for DOS namespace matches where only the MFT reference/type is needed.
