# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar.c

Implements core PostScript text operators and shared show-enumerator control flow.

Key behavior:
- Operators include `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `stringwidth`, `charpath`, `.charboxpath`, `setcachedevice`, `setcachedevice2`, `setcharwidth`, and `.fontbbox`.
- `finish_stringwidth` pushes accumulated text width and is reused by `.glyphwidth`.
- `op_show_finish_setup` records show state on the execution stack, including operand/dictionary stack depths, graphics state level, saved fonts, end procedure, and text enumerator.
- `op_show_continue_dispatch` handles normal completion, kshow intervention, character rendering through `BuildChar`/`BuildGlyph`, and CID/TrueType CDevProc cache setup.
- `op_show_return_width` short-circuits BuildChar/BuildGlyph execution when only width is needed and the font type is safe.
- `op_show_restore` frees text enumerators, restores currentfont, unwinds extra gstates, frees replacement-width arrays, and repairs stacks on error.
- `font_bbox_param` tolerates missing/invalid FontBBox and filters unreasonable boxes.

Dependencies and coupling:
- Central runtime used by `zcfont.c`, `zcharx.c`, `zchar1.c`, `zchar42.c`, and `zcharout.c`.
- Couples PostScript procedures with `gs_text_enum_t` and graphics-library text processing.
- Handles CID cshow special cases and composite-font current glyph propagation.
