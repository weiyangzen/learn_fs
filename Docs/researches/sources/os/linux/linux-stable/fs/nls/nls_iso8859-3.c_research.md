# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-3.c

Purpose: Generated Linux NLS module for ISO 8859-3 / Latin-3, described as Esperanto, Galician, Maltese, and Turkish.

Core structures and data:
- `charset2uni[256]` maps ISO 8859-3 bytes to Unicode and has explicit `0x0000` gaps for undefined byte positions.
- Reverse maps include `page00`, `page01`, and `page02`.
- Case conversion tables include defined Latin-3 case pairs and zeros for undefined byte positions.

Important behavior:
- `uni2char()` emits one byte for exact mapped Unicode values.
- `char2uni()` rejects bytes whose `charset2uni` entry is `0x0000`, including undefined bytes and NUL.
- The registered charset name is `"iso8859-3"`.

Dependencies and interfaces:
- Standard NLS registration with self-contained generated tables.

Design notes and risks:
- This charset has more undefined byte slots than Latin-1/2; callers should expect `-EINVAL` for those bytes.
- Lower/upper tables preserve undefined slots as zero, which can matter for consumers using case tables directly.
