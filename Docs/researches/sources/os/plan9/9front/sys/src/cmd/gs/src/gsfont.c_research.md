# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.c

## Role

`gsfont.c` implements generic Ghostscript font directory, font allocation, scaled-font caching, current font state, font cache parameters, font purging, default font procedure vectors, and default glyph metadata operations.

This is font/text rendering infrastructure, not filesystem code.

## Main Interfaces

- Font directory allocation:
  - `gs_font_dir_alloc2`
  - `gs_font_dir_alloc2_limits`
- Font allocation:
  - `gs_font_alloc`
  - `gs_font_base_alloc`
- Font notification:
  - `gs_font_notify_init`
  - `gs_font_notify_register`
  - `gs_font_notify_unregister`
- Font definition/scaling:
  - `gs_definefont`
  - `gs_font_find_similar`
  - `gs_scalefont`
  - `gs_makefont`
- Current font state:
  - `gs_set_currentfont`
  - `gs_setfont`
  - `gs_currentfont`
  - `gs_rootfont`
- Cache state:
  - `gs_cachestatus`
  - `gs_setcachesize`
  - `gs_setcachelower`
  - `gs_setcacheupper`
  - `gs_setaligntopixels`
  - `gs_setgridfittt`
  - matching current-value accessors
- Purge/lookup:
  - `gs_purge_font`
  - `gs_find_font_by_id`
- Default font/glyph procedures:
  - `gs_no_define_font`
  - `gs_no_make_font`
  - `gs_base_make_font`
  - `gs_default_font_info`
  - `gs_default_same_font`
  - `gs_base_same_font`
  - `gs_font_glyph_is_notdef`
  - dummy encode/decode/enumerate/outline/name procedures
  - `gs_default_glyph_info`

## Core Behavior

The font directory owns original base fonts, scaled-font cache entries, and the rendered character cache. Large cache limits are attempted first unless running in small-memory mode, with fallback to smaller defaults.

Scaled fonts are cached for non-composite fonts by base font and exact `FontMatrix`. Composite fonts are deliberately not cached because `makefont` can mutate descendant font state.

GC handling is specialized:

- base-font list pointers are weak during mark
- base fonts unlink themselves from the original-font list during finalization
- scaled fonts unlink from the scaled-font cache
- character-cache references to font/matrix pairs are enumerated and relocated through the font directory descriptor

## Important Details

- `gs_makefont` returns `0` when an existing scaled font is reused and `1` when a new scaled font is created.
- `gs_purge_font` recursively purges scaled descendants and clears character-cache entries.
- Font notification lists are allocated in stable memory to survive save/restore interactions.
- Default glyph info may build a path to derive widths and bounding boxes.

## Notable Risks

- Scaled-font cache eviction unlinks old fonts but cannot free them because outside references may exist.
- `gs_font_find_similar` has a spelling typo in its comment but not behavior.
- Exact matrix equality is used for cache hits.
- Some default glyph metadata depends on expensive outline path construction.
