# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gb.h

Defines GB2312 table bounds and exposes the GB mapping table.

Key points:
- Comment states GB ranges from `a1a1` to `f7fe` inclusive.
- Uses a kuten-like mapping from that range to ordinals `101-8794`.
- Defines `GBMAX` as `8795`.
- Declares `extern long tabgb[GBMAX]`.

Dependencies and interactions:
- Included by `gb.c`, `conv_gb.c`, and `font/gmap.c`.

Research relevance:
- Small public contract for the GB2312 mapping table.
