# File Research: sources/os/linux/linux/fs/nls/nls_ascii.c

Implements the `ascii` NLS codepage module.

Key behavior:
- Defines a 7-bit ASCII `charset2uni` table for bytes `0x00` through `0x7f`; bytes above `0x7f` default to `0x0000` and are invalid.
- Reverse lookup is only populated for Unicode page `00`.
- `uni2char()` returns one byte for exact ASCII mappings except NUL, and rejects unmappable values.
- `char2uni()` rejects byte `0x00` because it maps to `0x0000`.
- Provides ASCII lower/upper case conversion tables for `A-Z` and `a-z`.
- Registers charset name `ascii`.

Important interactions:
- Used as a minimal NLS table for filesystems needing strict ASCII filename conversion.
- Module lifecycle is standard `register_nls()` on init and `unregister_nls()` on exit.
