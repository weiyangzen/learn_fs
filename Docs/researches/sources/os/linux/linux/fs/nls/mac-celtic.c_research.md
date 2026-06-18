# File Research: sources/os/linux/linux/fs/nls/mac-celtic.c

Implements the `macceltic` NLS codepage module.

Main structure:
- Generated Unicode mapping data from Unicode Organization tables.
- `charset2uni[256]` maps single-byte Mac Celtic characters to Unicode.
- Reverse Unicode-to-charset pages include page tables for `0x00`, `0x01`, `0x03`, `0x1e`, `0x20`, `0x21`, `0x22`, `0x25`, and `0x26`.
- `charset2lower[256]` and `charset2upper[256]` are present but filled with sentinel values rather than meaningful case-folding mappings.
- `uni2char()` maps a Unicode codepoint to one byte or returns `-ENAMETOOLONG` / `-EINVAL`.
- `char2uni()` maps one byte to Unicode or returns `-EINVAL` for `0x0000`.
- Registers `struct nls_table` with charset name `macceltic`.

Lifecycle:
- `init_nls_macceltic()` calls `register_nls(&table)`.
- `exit_nls_macceltic()` calls `unregister_nls(&table)`.
- Declares module description `NLS Codepage macceltic` and license `Dual BSD/GPL`.

Risk notes:
- NUL byte maps to Unicode zero, and `char2uni()` treats zero as invalid. This is consistent with many Linux NLS tables for filename handling but matters to callers expecting raw byte round trips.
