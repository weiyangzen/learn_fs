# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/hdr.h

Declares the small font-generation helper interface.

Key points:
- Defines `readbitsfn`, the bitmap-reader function type.
- Defines `mapfn`, the Unicode-range-to-source-ordinal mapper type.
- Declares readers: `kreadbits`, `breadbits`, `greadbits`, and `qreadbits`.
- Declares mappers: `kmap`, `bmap`, and `gmap`.
- Declares `bf`, the helper that builds a `Subfont`.

Dependencies and interactions:
- Included by all source files in `tcs/font` except `merge.c`.
- Supports the dispatch table in `font/main.c`.

Research relevance:
- Compact local API for the font-conversion utility.
