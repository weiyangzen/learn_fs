# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccman.c

Implements Ghostscript character-cache management for font/matrix pairs, xfont lookup, cached glyph bitmap allocation, bitmap post-processing, and cache purging.

Key behavior:
- Allocates the font directory's font/matrix cache and open-addressed cached-character hash table, rounding the table to a power-of-two size with extra slack.
- Initializes cache chunks through the generic bits-cache layer and resets all `cached_fm_pair` entries, including TrueType reader/font pointers.
- Adds font/matrix pairs using `gx_compute_ccache_key`; when full, prefers evicting a pair with no cached characters and otherwise purges the selected pair.
- For Type 42/CID TrueType fonts without FAPI, creates a TrueType reader and helper font object tied to the scaled character matrix.
- Looks up xfonts through the current device's xfont device/procs, trying key name, font name, and original fonts with matching UID; stroked fonts are excluded.
- Purges selected cached characters by scanning the hash table, removing matching entries, freeing their bits, and preserving open-addressing lookup correctness by relocating following entries.
- Allocates character bitmap storage for mono or alpha-buffer cache devices, checking scaled-down size against cache limits and setting up memory devices in-place while preserving reference-count metadata.
- Adds rendered character bits by finding the non-white bounding box, trimming whitespace, compressing oversampled bitmaps to the requested alpha depth, adjusting offsets, shortening the bits-cache block, and assigning a fresh bitmap id.
- Frees and shortens cached characters through the shared bits-cache chunk machinery; chunk cycling can evict older entries to make room.
- Purges all cache references to a font, retaining UID-valid font/matrix entries by clearing their font pointer and fully purging others.

Dependencies:
- Uses Ghostscript memory/GC descriptors, font-directory and character-cache structures from `gxfcache.h`, memory devices from `gxdevmem.h`, font internals from `gxfont*.h`, xfont hooks from `gxxfont.h`, and TrueType helpers from `gxttfb.h`/`gxfont42.h`.
- Uses `gs_next_ids` for cached bitmap ids and generic bits-cache allocation/free/shorten operations.

Research notes:
- Cache correctness depends on keeping the character hash table and `cached_fm_pair::num_chars` synchronized during eviction and purge.
- `gx_add_char_bits` mutates bitmap dimensions and offsets after rendering, so callers must not assume the cache device's temporary dimensions survive unchanged.
- The xfont path stores the graphics state's memory in the pair because xfonts can outlive a single lookup and must be released on purge.
