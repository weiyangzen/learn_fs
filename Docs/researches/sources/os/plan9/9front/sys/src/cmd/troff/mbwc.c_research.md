# File Research: sources/os/plan9/9front/sys/src/cmd/troff/mbwc.c

Read completely: 22 lines, 400 bytes.

Compatibility implementation of `mbtowc` for Plan 9 runes. It decodes a UTF sequence into a `Rune` with `chartorune`.

Key behavior:
- If `s == nil`, returns 0.
- If `len <= 0`, returns -1.
- Calls `chartorune`; returns -1 when decoded byte count exceeds supplied length.
- Stores decoded rune through `rp` and returns byte length.

Dependencies:
- Includes `<u.h>` and `<libc.h>`.

Reliability notes:
- This is minimal and does not implement full C library conversion state; it is enough for the local troff code paths.
