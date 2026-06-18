# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccache.c

Implements fast character-cache lookup, external-font character lookup, cached-character imaging, and alpha-mask compression.

Key behavior:
- Computes font/matrix cache keys from character transformation matrices and log2 oversampling scales.
- Special-cases TrueType design-grid cache keys to zero matrix values because a single TrueType face cannot generate grid-fitted and non-grid-fitted outlines from the same face instance.
- `gx_lookup_fm_pair` searches the font/matrix cache by font pointer or stable UID plus matrix/design-grid state, then adds a pair on miss.
- `gx_lookup_cached_char` hashes glyph/pair and matches subpixel origin, writing mode, and depth.
- `gx_lookup_xfont_char` queries external fonts for glyph names, external glyph IDs, metrics, and creates a cache entry for externally renderable glyphs.
- `gx_image_cached_char` renders cached characters through several paths: direct xfont rendering, xfont-to-cache bitmap rendering, device `fill_mask`, `copy_alpha`, `copy_mono`, or fallback imagemask rendering.
- Handles clipping by installing a temporary clipping device when a glyph falls outside the show enumerator's inner box but intersects the outer box.
- Converts multi-bit alpha character masks to monobit masks when the target path cannot consume alpha directly.
- `compress_alpha_bits` maps 2-bit/4-bit-ish cached alpha depth to a one-bit mask using the high-order alpha bit.

Dependencies:
- Integrates with Ghostscript show enumerators, font directories, font matrix cache, external font procs, devices, memory devices, clipping paths, image masks, halftone/device colors, and logical operations.
- Uses bitmap raster/alignment helpers from `gxbitmap.h` and cache structures from font-cache headers.

Research notes:
- `cc_depth` value 3 is treated as 2-bit alpha for a 4-by-2 text-antialiasing scale case.
- `gx_image_cached_char` treats VM allocation failure for temporary masks/image enums as recoverable by returning `1`.
- Direct xfont rendering is preferred when pure color output is possible, even over multi-bit cached bitmap rendering.
