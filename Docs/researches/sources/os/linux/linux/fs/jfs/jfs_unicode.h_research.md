# File Research: sources/os/linux/linux/fs/jfs/jfs_unicode.h

Declares Unicode conversion APIs and provides inline UCS string helpers for JFS.

Exports:
- `get_UCSname()` allocates/converts a dentry name to JFS UCS form.
- `jfs_strfromUCS_le()` converts little-endian on-disk UCS strings to byte strings.
- `free_UCSname()` frees a `component_name` buffer.

Inline helpers:
- `UniStrcpy()` copies native `wchar_t` strings.
- `UniStrncpy_le()` copies/pads little-endian UCS strings.
- `UniStrncmp_le()` compares native UCS against little-endian UCS.
- `UniStrncpy_to_le()` and `UniStrncpy_from_le()` convert while copying/padding.
- `UniToupper()` uppercases using Linux UCS-2 NLS tables.
- `UniStrupr()` uppercases an in-place native UCS string.

Integration:
- Used by directory name comparison, case folding, dentry conversion, and on-disk directory entry handling.
