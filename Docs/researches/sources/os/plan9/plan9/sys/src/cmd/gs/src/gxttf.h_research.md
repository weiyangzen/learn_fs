# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttf.h

TrueType table layout header. It defines byte-accurate structures and flags used to parse TrueType font data.

Key contents:
- Composite glyph flags such as `TT_CG_ARGS_ARE_WORDS`, `TT_CG_ARGS_ARE_XY_VALUES`, `TT_CG_HAVE_SCALE`, `TT_CG_MORE_COMPONENTS`, `TT_CG_HAVE_XY_SCALE`, `TT_CG_HAVE_2X2`, `TT_CG_HAVE_INSTRUCTIONS`, and `TT_CG_USE_MY_METRICS`.
- Table structures for `head`, `hhea`, `hmtx` long horizontal metrics, `maxp`, `OS/2`, `vhea`, and `vmtx` long vertical metrics.
- Fields are stored as `byte` arrays matching the big-endian on-disk TrueType representation rather than native integers.

Research notes:
- This header is a data-layout contract, not a parser.
- Consumers must decode multi-byte fields explicitly; direct native integer access would be incorrect.
