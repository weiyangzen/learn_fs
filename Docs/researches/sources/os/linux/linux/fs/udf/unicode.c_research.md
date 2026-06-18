# File Research: sources/os/linux/linux/fs/udf/unicode.c

Purpose: conversion between UDF OSTA Compressed Unicode CS0 and Linux filenames.

Key behavior:
- Decodes compressed Unicode with 8-bit or 16-bit compression IDs.
- `get_utf16_char()` handles UTF-16 surrogate pairs and rejects malformed surrogate sequences.
- `udf_name_from_CS0()` converts CS0 to UTF-8 or configured NLS charset, optionally translating illegal chars and `/` to `_`, preserving short extensions when possible, and appending a 5-character CRC marker when names are truncated or mangled.
- `udf_name_to_CS0()` converts UTF-8 or NLS input to CS0, switching from 8-bit to 16-bit encoding when required and encoding non-BMP characters as surrogate pairs.
- `udf_dstrCS0toChar()` converts informational UDF dstrings, truncating invalid recorded lengths rather than failing mount.
- `udf_get_filename()` and `udf_put_filename()` are directory/symlink-facing wrappers.

Integration:
- Used by UDF lookup, directory entry creation, symlink conversion, and superblock volume identifier decoding.
- Uses NLS table from `UDF_SB(sb)->s_nls_map`; absence means UTF-8.

Risks and invariants:
- Zero-length decoded filenames are invalid for directory names.
- Unknown compression code and malformed length return `-EINVAL`.
- CRC mangling avoids collisions when names contain illegal/unrepresentable chars or exceed output length.
