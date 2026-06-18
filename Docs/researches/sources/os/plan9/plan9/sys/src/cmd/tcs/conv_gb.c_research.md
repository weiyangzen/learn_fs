# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gb.c

GB2312 input/output converter for `tcs`.

Key functions:
- `gbproc` decodes two-byte GB sequences where both bytes are `>= 0xA1`; ordinal is `(lead-0xA0)*100 + (trail-0xA0)`.
- `gb_in` streams input bytes through `gbproc`.
- `gb_out` builds reverse mapping from `tabgb`, emits ASCII directly, and emits two-byte GB for mapped runes.

Error behavior:
- Invalid second byte or unmapped table entry records errors and optionally emits replacement mappings depending on `clean`.

Dependencies:
- `hdr.h`, `conv.h`, `gb.h`, global `tabgb`/`GBMAX`.
