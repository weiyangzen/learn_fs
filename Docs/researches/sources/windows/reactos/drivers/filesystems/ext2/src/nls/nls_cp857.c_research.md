# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp857.c

Purpose: Generated NLS module for DOS/OEM code page 857, covering Turkish-oriented Latin characters for Ext2 filename conversion.

Core structures and data:
- `charset2uni[256]` includes Latin-1-like accented letters, Turkish `U+0130`, `U+0131`, `U+011E`, `U+011F`, `U+015E`, `U+015F`, box drawing, and several explicit `0x0000` undefined slots.
- Reverse pages `page00`, `page01`, and `page25` map supported Unicode back to CP857.
- `charset2lower` and `charset2upper` include ASCII and Turkish-specific case pairs, with zeros preserved for undefined bytes.

Important behavior:
- `uni2char()` emits exactly one byte for exact mappings and fails with `-EINVAL` for unmapped Unicode.
- `char2uni()` rejects undefined byte positions because their forward table entries are `0x0000`.
- The registered charset name is `"cp857"` with no alias.

Dependencies and interfaces:
- Self-contained `struct nls_table` module using the same Linux NLS callback contract as the neighboring generated codepage files.
- No runtime dependency on another charset.

Design notes and risks:
- Turkish dotted/dotless I behavior is represented only by byte lookup tables, not by locale-aware Unicode case logic.
- Undefined byte slots affect both conversion and case tables; consumers using casefold arrays directly may see zero for those positions.
- The single-byte callback skeleton cannot encode Unicode NUL because zero is the unmapped sentinel.
