# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.c

## Role

`gsgcache.c` implements a small glyph data cache for Type 42 fonts, primarily when emulating CIDFontType 2 using TrueType data.

This is glyph/font cache infrastructure, not filesystem code.

## Main Interfaces

- `gs_glyph_cache__alloc`
- `gs_glyph_cache__release`
- `gs_get_glyph_data_cached`

## Core Behavior

The cache stores linked `gs_glyph_cache_elem` entries containing glyph data, glyph index, lock count, and next pointer.

Cache allocation:

- uses the font’s stable memory
- records the stream and read callback
- registers a font-free notification callback

Lookup:

- returns cached data if present
- otherwise reuses an unlocked element when cache size is above an arbitrary threshold
- otherwise allocates a new head element
- loads glyph data through the supplied `read_data` callback
- returns a borrowed glyph data view with custom free/substring procs

Release:

- frees every cached glyph data object
- unregisters font notification
- frees the cache object

## Important Details

- The cache is hardcoded to Type 42 use.
- Cache entries are lock-counted while clients hold returned glyph data.
- The substring proc for cached glyph data is unsupported and returns `unregistered`.

## Notable Risks

- If `read_data` fails after allocating or reusing an element, the function returns without clearly removing or resetting the partially prepared element.
- The cache size threshold `32767` is arbitrary.
- `total_size` accounting is simple and only adjusted on reuse/free paths.
