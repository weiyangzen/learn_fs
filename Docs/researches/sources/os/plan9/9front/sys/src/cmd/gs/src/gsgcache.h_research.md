# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.h

## Role

`gsgcache.h` declares the glyph data cache API used by Type 42 glyph loading.

This is font cache API infrastructure, not filesystem code.

## Main Types

- forward declarations:
  - `gs_font_type42`
  - `gs_glyph_data_t`
  - `stream`
  - `gs_glyph_cache`
- `get_glyph_data_from_file`

## Public API

- `gs_glyph_cache__alloc`
- `gs_glyph_cache__release`
- `gs_get_glyph_data_cached`

## Important Contract

The cache is constructed with a Type 42 font, a stream, and a callback that can load glyph data from that stream.
