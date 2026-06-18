# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-3.c

Purpose: Generated Linux NLS module for ISO 8859-3 / Latin-3, described as Esperanto, Galician, Maltese, and Turkish.

Core structures and data:
- `charset2uni[256]` has explicit `0x0000` gaps for undefined byte positions.
- Reverse mappings include `page00`, `page01`, and `page02`.
- Case tables preserve undefined byte slots as zero.

Important behavior:
- `uni2char()` emits one byte for exact represented Unicode code points.
- `char2uni()` rejects undefined bytes and NUL through the zero-sentinel convention.
- Registers charset `"iso8859-3"`.

Dependencies and interfaces:
- Standard self-contained NLS registration.

Design notes and risks:
- This charset has more undefined byte slots than Latin-1/2.
- Consumers using case tables directly must account for zero entries on undefined bytes.
