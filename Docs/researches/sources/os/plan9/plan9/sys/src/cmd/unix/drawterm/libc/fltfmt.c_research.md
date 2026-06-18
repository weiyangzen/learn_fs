# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fltfmt.c

This file implements floating-point formatting for Plan 9 `Fmt`.

Key behavior:
- `__efgfmt` handles `%e`, `%f`, and `%g` style conversions.
- `floatfmt`, `xdtoa`, and decimal helpers produce rounded decimal representations.
- Local `pow10`, `xadd`, and `xsub` support decimal digit adjustment.

Important details:
- Handles NaN/Inf through helpers from `nan64.c`.
- Honors formatter width, precision, and flags.
