# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttf.h

Declares raw TrueType table layout structures and composite glyph flags.

Key contents:
- Composite glyph flags such as `TT_CG_ARGS_ARE_WORDS`, `TT_CG_HAVE_SCALE`, `TT_CG_MORE_COMPONENTS`, `TT_CG_HAVE_2X2`, and `TT_CG_USE_MY_METRICS`.
- Byte-array structs matching TrueType table layouts:
  - `ttf_head_t`
  - `ttf_hhea_t`
  - `longHorMetric_t`
  - `ttf_maxp_t`
  - `ttf_OS_2_t`
  - `ttf_vhea_t`
  - `longVerMetric_t`

Dependencies:
- Uses Ghostscript `byte` type supplied by the surrounding build headers.

Research notes:
- Fields remain encoded as raw big-endian byte arrays rather than host integers.
- This header is a structural table definition layer, not a parser or interpreter.
