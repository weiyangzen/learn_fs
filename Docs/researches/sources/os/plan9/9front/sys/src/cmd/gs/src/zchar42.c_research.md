# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.c

This file implements Type 42 and CID TrueType character display support.

Key behavior:
- `zchar42_set_cache` computes metrics for TrueType/Type 42 glyphs and calls common `zchar_set_cache`.
- Uses font Metrics when present; otherwise asks the Type 42 backend for horizontal and, when needed, vertical WMode metrics.
- Provides vertical fallback metrics for CID TrueType fonts when vertical TrueType metrics are unavailable.
- `.type42execchar` validates current show context and TrueType/CID TrueType font type, establishes a current point, sets cache, and then fills or strokes the glyph.
- `type42_finish` appends a TrueType glyph outline to the current path through `gs_type42_append` and draws it.

Important dependencies:
- Uses `gxfont42.h`, `gxtext.h`, `gspath.h`, `gspaint.h`, and common char output cache helpers.
- Declared externally in `zchar42.h`.

Research notes:
- Rendering deliberately uses current gstate/path rather than the text enumerator imager/path; the source calls this a design bug.
