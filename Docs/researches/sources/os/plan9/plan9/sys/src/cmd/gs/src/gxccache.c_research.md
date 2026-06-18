# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccache.c

Purpose: Implements fast-path character cache lookup and rendering routines for Ghostscript.

Key entry points:
- `gx_compute_char_matrix()` applies log2 oversampling scale to a character matrix.
- `gx_compute_ccache_key()` computes the font/matrix cache key, with special handling for design-grid TrueType.
- `gx_lookup_fm_pair()` finds or adds a cached font/matrix pair.
- `gx_lookup_cached_char()` finds a cached glyph bitmap by glyph, pair, subpixel origin, writing mode, and depth.
- `gx_lookup_xfont_char()` maps a glyph to an external font glyph and creates a cache entry.
- `gx_image_cached_char()` renders a cached character through fill-mask, copy-alpha, copy-mono, xfont, or imagemask paths.

Important internals:
- `scale_log2_1` is the default 1x scale.
- `compress_alpha_bits()` converts 2/4-bit alpha cached masks into 1-bit masks using high-order alpha bits.

Behavior:
- TrueType design-grid cache keys may be zero matrices because the TT interpreter cannot share one face instance for grid-fitted and non-grid-fitted outlines.
- Font/matrix lookup can use UID instead of font pointer for base fonts with valid UIDs.
- External xfont rendering is preferred when available and color conditions permit.
- If cached glyph bounds exceed the inner clip box, it wraps the target in a clipping device unless completely outside.
- For pure colors, tries `fill_mask`, `copy_alpha`, then `copy_mono`; otherwise falls back to imagemask rendering.

Dependencies:
- Uses font directory caches (`gxfcache.h`), xfont APIs, path/current point state, device procedures, memory devices, clipping, image enumeration, and bitmap raster helpers.

Notable risks:
- `compress_alpha_bits()` allocates temporary masks from non-GC memory and callers must free them on fallback paths.
- Several render paths return `1` as recoverable failure/VMerror-style fallback rather than hard error.
- Cache key and xfont behavior depend on subtle font type, UID, encoding, and writing-mode conditions.
