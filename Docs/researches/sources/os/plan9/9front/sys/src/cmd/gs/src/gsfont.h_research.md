# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.h

## Role

`gsfont.h` is the public generic font and font-cache interface for Ghostscript.

This is font API infrastructure, not filesystem code.

## Main Declarations

- Opaque types:
  - `gs_matrix`
  - `gs_font_dir`
  - `gs_font`
- Font directory allocation:
  - `gs_font_dir_alloc2`
  - `gs_font_dir_alloc2_limits`
  - backward-compatible macros using a single allocator
- Font operations:
  - `gs_definefont`
  - `gs_font_find_similar`
  - `gs_scalefont`
  - `gs_makefont`
  - `gs_setfont`
  - `gs_currentfont`
  - `gs_rootfont`
  - `gs_set_currentfont`
  - `gs_purge_font`
  - `gs_find_font_by_id`
- Cache operations:
  - `gs_cachestatus`
  - `gs_setcachesize`
  - `gs_setcachelower`
  - `gs_setcacheupper`
  - `gs_setaligntopixels`
  - `gs_setgridfittt`
  - matching query functions

## Important Contract

`gs_definefont` is for original unscaled fonts only. `gs_scalefont` and `gs_makefont` report whether a cached scaled font was reused or newly created.
