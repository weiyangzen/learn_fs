# File Research: sources/os/linux/linux/fs/jfs/jfs_unicode.c

Implements filename conversion between JFS on-disk little-endian UCS-2 and Linux dentry byte strings.

Functions:
- `jfs_strfromUCS_le()` converts little-endian UCS-2 to a character string. With an NLS table it uses `uni2char`; without one it falls back to Latin-1-compatible single-byte characters and substitutes `?` for non-Latin-1, warning up to five times globally.
- `jfs_strtoUCS()` converts byte strings to native `wchar_t` using `char2uni` when a codepage is mounted, or direct byte widening otherwise.
- `get_UCSname()` validates `JFS_NAME_MAX`, allocates a UCS buffer for a dentry name, converts it using the mounted NLS table, and returns errors for allocation or conversion failure.

Integration:
- Directory lookup/create paths use `component_name` values produced here.
- Mounted `iocharset`/NLS choice controls round-trip behavior for non-ASCII names.
