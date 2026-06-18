# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacxf.c

Implements Classic/Carbon MacOS external font (`xfont`) support for the `macos` device.

Key behavior:
- Defines encoding conversion tables for Standard-to-Mac and ISO-Latin-1-to-Mac.
- Declares but leaves `gs_map_mac_to_std` and `gs_map_mac_to_iso` as zero-initialized arrays.
- Defines `mac_xfont_procs` with lookup, char-to-xglyph, metrics, render, and release functions.
- Registers `mac_xfont` with Ghostscript GC metadata via `gs_private_st_dev_ptrs1`.
- `mac_get_xfont_procs` returns the static xfont procedure table.
- `mac_lookup_font`:
  - Requires `UseExternalFonts` to be enabled.
  - Accepts only MacRoman, ISO Latin-1, or Standard encodings.
  - Rejects tiny fonts and transformed matrices.
  - Allocates `mac_xfont`, finds a Mac font family/style, gets font name, size, encoding, and metrics.
  - Saves and restores current GrafPort text state while measuring.
- `mac_char_xglyph` maps input character codes through the encoding tables depending on the native font encoding.
- `mac_char_metrics` returns broad metrics from `FMetricRec`, with no per-glyph width lookup.
- `mac_render_char` emits PICT font-name/font/size/face opcodes when needed, then writes a `LongText` opcode for the single character.
- `mac_release` frees the xfont object.
- `mac_find_font_family` tries exact names, dash-to-space names, and then extracts style tokens like Italic, Bold, Narrow, and Condensed.
- `mac_get_font_encoding` loads the font resource, walks the TrueType directory, finds the naming table, and maps platform IDs to MacRoman or ISO Latin-1.
- `mac_get_font_resource` uses `FMSwapFont` and `GetResInfo`.
- Provides compatibility wrappers for older Font Manager APIs when `USE_RECOMMENDED_CARBON_FONTMANAGER_CALLS` is disabled.

Dependencies and notes:
- Depends on `gdevmac.h`, `gdevmacttf.h`, Classic/Carbon Font Manager APIs, QuickDraw GrafPort state, and Ghostscript xfont types.
- Some failure paths in `mac_lookup_font` return `NULL` after allocation without freeing `macxf`.
- Reverse encoding maps are empty, which limits MacRoman-to-ISO/Standard conversions.
