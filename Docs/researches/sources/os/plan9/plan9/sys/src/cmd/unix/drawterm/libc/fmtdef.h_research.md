# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtdef.h

This header defines internal formatting-library helpers.

Key contents:
- Declares internal `__fmt*`, quote, NaN/Inf, string, rune, and conversion functions.
- Defines `Quoteinfo`.
- Provides `FMTCHAR`, `FMTRCHAR`, and `FMTRUNE` buffered-output macros.
- Defines `VA_COPY` compatibility and `PLAN9PORT`.

Important details:
- Shared by nearly all formatting implementation files.
