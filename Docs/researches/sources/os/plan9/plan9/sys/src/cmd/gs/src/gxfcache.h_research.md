# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcache.h

Defines font, font/matrix pair, and character cache structures.

- Defines `cached_fm_pair`, the key for a base font plus transformation:
  - font pointer or UID/FontType
  - hash
  - matrix entries
  - cached character count
  - xfont lookup state
  - TrueType interpreter/reader pointers
  - design-grid flag
- UID-backed entries may survive font restore with `font == 0`.
- Nonzero `PaintType` fonts cannot be cached due to stroke-width dependency.
- Defines `fm_pair_cache`, an array/rover cache for font/matrix pairs.
- Defines `cached_char` as a subclass of the generic bitmap cache entry:
  - key fields include glyph code, pair, writing mode, and depth
  - value fields include bitmap data, xglyph, width, and offset
- Cached character bits immediately follow the `cached_char` structure.
- Real cached chars must have either bitmap bits or a valid xfont glyph.
- Defines unusual memory-management model:
  - `cached_char` objects live inside non-GC bitmap chunks.
  - The font directory traces/relocates pointers from the cache manually.
- Defines `char_cache`:
  - bitmap cache chunks
  - struct/bits allocators
  - open-addressed hash table
  - size limits
  - glyph marking callback
- Defines `gs_font_dir`, the font-directory/cache manager:
  - original fonts
  - scaled font cache
  - font/matrix cache
  - character cache
  - GC scan state
  - user params such as `AlignToPixels` and `GridFitTT`
  - glyph-to-Unicode and TrueType interpreter data
- Declares cache procedures:
  - `gx_char_cache_alloc`
  - `gx_char_cache_init`
  - `gx_purge_selected_cached_chars`
  - matrix/key computation helpers
  - font/matrix lookup/add
  - xfont lookup
  - purge helpers

Role: core data model for Ghostscript glyph caching and font-directory GC integration.
