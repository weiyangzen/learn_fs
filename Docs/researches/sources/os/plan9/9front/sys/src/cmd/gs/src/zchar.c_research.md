# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar.c

This is the main Ghostscript character rendering operator file.

Key behavior:
- Implements `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `stringwidth`, `charpath`, `.charboxpath`, `setcachedevice`, `setcachedevice2`, and `setcharwidth`.
- Builds and drives `gs_text_enum_t` text enumerators for rendering, measuring, kerning, charpath construction, and cache-device setup.
- Stores show state on the e-stack, including saved operand/dictionary stack depths, graphics-state level, current/root font state, and cleanup procedure.
- Dispatches text processing outcomes:
  - normal completion
  - kshow/cshow intervention
  - BuildChar/BuildGlyph rendering
  - CDevProc cache setup for CID Type 0 and CID TrueType fonts
  - error cleanup
- Chooses BuildChar versus BuildGlyph based on font type, glyph availability, character code, and Encoding equality.
- Implements glyph-to-character reverse lookup for Type 3 `glyphshow` fallback.
- Provides `font_bbox_param`, tolerating missing or unreasonable FontBBox values by zeroing them.

Important dependencies:
- Works with `gstext`, `gxfont`, `gxfont42`, `gxfont0`, `ichar`, `ichar1`, `ifont`, `igstate`, `estack`, and dictionary stack APIs.
- Calls specialized cache helpers from `zchar42.h` and Type 1 helper `z1_set_cache`.

Research notes:
- This file is the core interpreter lifecycle for text rendering and text measurement.
- It is careful about error cleanup because BuildChar/BuildGlyph can execute arbitrary PostScript and mutate stacks/gstate.
