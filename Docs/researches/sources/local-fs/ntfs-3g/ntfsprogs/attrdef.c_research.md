# File Research: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.c

Defines `attrdef_ntfs3x_array`, a 2560-byte static binary image used by `mkntfs` as the default NTFS 3.x `$AttrDef` file contents. The array encodes fixed-size NTFS attribute-definition records with UTF-16LE names and metadata for standard NTFS attributes.

The embedded records include definitions for `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, `$FILE_NAME`, `$OBJECT_ID`, `$SECURITY_DESCRIPTOR`, `$VOLUME_NAME`, `$VOLUME_INFORMATION`, `$DATA`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, `$REPARSE_POINT`, `$EA_INFORMATION`, `$EA`, and `$LOGGED_UTILITY_STREAM`.

There is no executable logic in this file beyond exporting the constant data declared in `attrdef.h`. Correctness depends on the byte image matching the NTFS layout expected by `mkntfs` and Windows-compatible NTFS 3.x volumes.
