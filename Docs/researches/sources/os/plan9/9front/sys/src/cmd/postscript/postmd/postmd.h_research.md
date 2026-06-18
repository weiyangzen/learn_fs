# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.h

`postmd.h` defines matrix interval-list defaults and the `Ilist` structure for `postmd.c`.

Key contents:
- `DFLTILIST` is `"-1,0,1"`, producing seven mapping regions by default.
- Comments explain how an ordered interval list partitions the real line into alternating less-than/equality regions.
- Comments also describe grayscale override lists, where colors map to regions and default values fill missing entries.
- `Ilist` contains:
  - `double val` for endpoint values,
  - `int color` for grayscale byte output,
  - `long count` for per-region statistics.
- Declares non-integer function `savestring()`.

This header is documentation-heavy and directly supports the matrix-to-grayscale mapping in `postmd.c`.
