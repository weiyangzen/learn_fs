# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp874.c

Purpose: Generated NLS module for Windows/DOS code page 874, Thai, with a `tis-620` alias.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes, selected punctuation in the `0x80-0x9f` range, Thai letters and marks `U+0E01..U+0E5B`, Thai baht sign `U+0E3F`, and undefined zero slots.
- Reverse pages `page00`, `page0e`, and `page20` map Latin/punctuation, Thai, and punctuation marks back to CP874.
- `charset2lower` and `charset2upper` mostly preserve bytes because Thai has no case; ASCII folding remains present.
- `table.alias` is `"tis-620"`, and `MODULE_ALIAS_NLS(tis-620)` advertises the alias.

Important behavior:
- `uni2char()` emits a single byte for exact CP874/TIS-620-compatible mappings.
- `char2uni()` rejects undefined bytes and NUL through zero-valued `charset2uni` entries.
- Module init registers charset `"cp874"`.

Dependencies and interfaces:
- Self-contained Linux NLS table with standard module registration.
- No Thai shaping, collation, or normalization support appears in the file.

Design notes and risks:
- The alias makes CP874 available to consumers requesting `tis-620`, but the table also includes Windows punctuation mappings outside strict simple Thai letter ranges.
- Undefined byte slots around C1 controls and Thai gaps intentionally fail.
- Case tables are not meaningful for Thai letters beyond identity mapping.
