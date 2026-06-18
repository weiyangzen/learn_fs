# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.h

## Role

Public declaration for the glyph data cache.

## Main Data

Forward-declares Type42 font, glyph data, stream, and glyph cache types. Defines callback type `get_glyph_data_from_file`.

## Main API

Declares `gs_glyph_cache__alloc`, `gs_glyph_cache__release`, and `gs_get_glyph_data_cached`.

## Dependencies

Relies on Type42 font and stream abstractions.

## Notes

The interface is written for cached access to Type42 glyph outlines, with the cache object stored behind an opaque `gs_glyph_cache` pointer.
