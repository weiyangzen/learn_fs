# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_unicode.h

## Role

Declares JFS Unicode conversion functions and provides inline UCS string utilities.

## Key Definitions

- Public functions:
  - `get_UCSname()`
  - `jfs_strfromUCS_le()`
- `free_UCSname()` frees a component name buffer.
- `UniStrcpy()` copies native `wchar_t` strings.
- `UniStrncpy_le()` copies/pads little-endian UCS strings.
- `UniStrncmp_le()` compares native `wchar_t` to little-endian UCS.
- `UniStrncpy_to_le()` and `UniStrncpy_from_le()` convert fixed-length strings to/from little-endian UCS.
- `UniToupper()` uppercases using Linux NLS Unicode case tables.
- `UniStrupr()` uppercases a whole native Unicode string.

## Design Notes

The header bridges JFS directory/name code with Linux NLS tables and little-endian on-disk name storage.
