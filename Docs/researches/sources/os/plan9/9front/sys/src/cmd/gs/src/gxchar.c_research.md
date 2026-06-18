# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.c

Default Ghostscript text rendering implementation. It drives show/stringwidth/charpath processing, cached glyph lookup and creation, xfont fallback, text positioning, and BuildChar/BuildGlyph continuation.

Key behavior:
- Defines the GC-visible `gs_show_enum` descriptor and default `gs_text_enum_procs` for resync, process, width-only query, current-width query, cache setup, retry, and release.
- `gx_default_text_begin` validates that the imager state is a full `gs_state`, initializes the text enumerator, derives charpath/cache policy from the requested text operation, prepares state, and installs a null device for stringwidth.
- `gx_hld_stringwidth_begin` gives pdfwrite a helper path/current-point setup for Type 3 stringwidth handling.
- `gx_show_text_set_cache` handles `setcharwidth`, `setcachedevice`, and `setcachedevice2`, including WMode 1 origin adjustment and retry rewinding.
- `set_char_width` transforms character advance to device coordinates and has special CID encrypted font handling to avoid applying a leaf FontMatrix to CDevProc widths.
- Computes raster parameters from device text alpha bits, font PaintType, pure-color status, FAPI-provided scale, current origin, and pixel-alignment mode.
- `set_cache_device` decides whether a glyph can be cached, transforms the font bounding box to device space, rejects very large or invalid entries, allocates cache memory devices, clips user-defined fonts when needed, and redirects rendering into the cache device.
- The continuation pipeline uses `show_proceed`, `show_update`, and `show_move` to alternate between cache hits, direct BuildChar calls, intervention returns for cshow/kshow, and final movement.
- Cache-hit handling can image cached glyphs, append cached bounding boxes for charboxpath, or short-circuit charwidth/stringwidth.
- Cache-miss handling saves graphics state, switches to the descendant font when needed, sets charpath mode, adjusts the CTM/current origin into character space, then calls the font's build procedure.
- `show_update` finishes a cached render by adding the cached character to the font cache, restoring graphics state levels, loading color, and optionally imaging the just-created cache entry.
- `gx_show_text_retry` discards a partially cached glyph and restores state so character rendering can be retried.
- `show_state_setup` refreshes current font/matrix state after start, font changes, and kshow callbacks; it records clipping boxes, transformed font translation, and cache eligibility.
- `show_set_scale` selects oversampling for small non-skewed outline characters, scaling both axes when oversampling is used.
- Releases retained cache and null devices before delegating to the default text-enum release path.

Dependencies:
- Uses graphics state internals, matrix/path operations, memory and null devices, font stacks/composite fonts, font cache APIs from `gxchar.h`/`gxfcache.h`, and CID font helpers.
- Calls cache-manager functions from `gxccman.c` and cache lookup/imaging routines implemented elsewhere.

Research notes:
- This file is continuation-oriented: many public text operations return intermediate statuses rather than rendering an entire string in one call.
- Cache decisions are deliberately conservative around charpath modes, modified CTMs, non-pure colors, stroked fonts, alpha, clipping, and oversized glyphs.
- Correct graphics-state level accounting is central: BuildChar procedures may save/restore, and `show_update` validates the resulting save depth.
