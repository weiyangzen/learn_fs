# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.h

Internal character and text-show declarations for Ghostscript.

Key definitions:
- Forward-declares cached characters, cached font/matrix pairs, fonts, text enumerators, memory devices, and null devices.
- Defines `show_width_status` values used while BuildChar communicates width and cache-device choices.
- Defines `gs_show_enum_s`, a subclass of `gs_text_enum_common`, with graphics state pointers, charpath mode, cache permissions, clipping boxes, transformed font translation, encoding callback, FAPI scaling data, cache/null devices, current width/origin, active cached character, and continuation callback.
- Provides the public structure descriptor macro for `gs_show_enum`.

Key declarations:
- Text accessors: `gx_current_char`, `gx_compute_text_oversampling`, `set_char_width`, `gx_default_text_restore_state`, and `gx_hld_stringwidth_begin`.
- Cached-character lifecycle and lookup APIs: allocate/open/free/add bits, add cache entry, lookup cached glyph, lookup xfont glyph, and image cached glyph.

Dependencies:
- Requires `gschar.h` and `gxtext.h`; comments note that matrix and fixed-point definitions must already be visible.

Research notes:
- The struct layout is part of the internal text-rendering contract; BuildChar and cache code rely on fields such as `width_status`, `cc`, `pair`, `log2_scale`, and `continue_proc`.
- `can_cache` distinguishes no cache use, read-only cache use, and full read/write cache use.
