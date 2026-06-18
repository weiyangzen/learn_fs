# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.h

Local definitions for the matrix-display translator.

Contents:
- Defines default interval list `DFLTILIST "-1,0,1"`.
- Documents interval-to-region mapping and grayscale override behavior.
- Defines `Ilist` structure:
  - `double val`
  - `int color`
  - `long count`
- Declares `char *savestring()`.

Role:
- Provides the interval-list data model used by `postmd.c` to classify floating-point matrix elements and build legend/statistics output.

Risks and quirks:
- Comments describe equality regions as separate buckets; exact floating-point equality is therefore semantically significant.
- No size constants are defined here for `ilist`; the implementation hardcodes `ilist[128]`.
