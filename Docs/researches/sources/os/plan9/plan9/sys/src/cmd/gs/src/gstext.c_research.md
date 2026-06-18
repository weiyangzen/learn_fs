# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.c

## Purpose
Implements Ghostscript's generic driver text interface support. It validates text parameters, initializes and manages text enumerators, wraps PostScript-equivalent text operators, updates device color, forwards text processing through enumerator procedure tables, and supplies default font callbacks.

## Public Surface
- Text begin APIs: `gx_device_text_begin`, `gs_text_begin`.
- Enumerator initialization/copy: `gs_text_enum_init`, `gs_text_enum_copy_dynamic`.
- PostScript-equivalent begin wrappers: `gs_show_begin`, `gs_ashow_begin`, `gs_widthshow_begin`, `gs_awidthshow_begin`, `gs_kshow_begin`, `gs_xyshow_begin`, `gs_glyphshow_begin`, `gs_cshow_begin`, `gs_stringwidth_begin`, `gs_charpath_begin`, `gs_charboxpath_begin`, `gs_glyphpath_begin`, `gs_glyphwidth_begin`.
- Processing APIs: `gs_text_restart`, `gs_text_resync`, `gs_text_process`, `gs_text_update_dev_color`.
- Accessors: current font/char/glyph, next char, total width, replaced width, width-only test, current width.
- Cache APIs: `gs_text_set_cache`, `gs_text_setcharwidth`, `gs_text_setcachedevice`, `gs_text_setcachedevice2`, `gs_text_retry`.
- Release/defaults: `gx_default_text_release`, `rc_free_text_enum`, `gs_text_release`, `gs_default_init_fstack`, `gs_default_next_char_glyph`, `gs_no_build_char`.

## GC Support
- `public_st_gs_text_params` enumerates the active input pointer based on `TEXT_FROM_*` flags and width arrays when `TEXT_REPLACE_WIDTHS` is set.
- `public_st_gs_text_enum` enumerates device pointers, imager state, fonts, path, device color, clip path, font-cache pair base, font stack entries, and embedded text parameters.
- Relocation handles device pointer relocation, embedded parameter relocation, font stack entries, and cached pair pointers that may point into an array element.

## Control Flow
- `gx_device_text_begin` rejects invalid operation masks, strips path/clip arguments when not needed, and calls the device's `text_begin` procedure.
- `gs_text_begin` computes effective clip path for drawing, loads the current device color even for width-only operations because high-level devices may accumulate Type 3 charstrings, and calls `gx_device_text_begin`.
- `gs_text_enum_init` copies immutable text parameters and common context into the enumerator, initializes dynamic state through the font's `init_fstack`, and increments the device reference.
- `gs_text_enum_copy_dynamic` copies current font, indices, font stack, metrics hints, cached pair pointer, and optional returned data for subsidiary enumerators.
- Operator wrappers build a `gs_text_params_t` with appropriate source, width adjustment, draw/path/width flags, and pass it to `gs_text_begin`.
- `text_do_draw` maps text rendering mode 3 to `TEXT_DO_NONE`, otherwise drawing.
- Restart/resync/processing/cache operations dispatch through `pte->procs`.

## Character Handling
- `gs_default_next_char_glyph` reads the next item from string/bytes/chars/glyphs/single-char/single-glyph sources, increments `pte->index`, and returns 2 at end.
- Glyph-based operations set `FontBBox_as_Metrics2` for CID encrypted/TrueType fonts to support metrics fallback.

## Dependencies
Depends on devices, fonts, font cache, paths, device colors, graphics state internals, and text enumerator definitions in `gxtext.h`.

## Risks and Notes
- Text rendering itself is not implemented here; device/font-specific enumerator procedures do the actual processing.
- The code intentionally loads device color for stringwidth-like operations because high-level Type 3 accumulation can need color despite no visible drawing.
