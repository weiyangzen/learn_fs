# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcache.h

This header defines Ghostscript font/matrix and character cache structures plus font-directory cache management APIs. It depends on font identity, xfont, bitmap cache, fixed-point, and font-type headers.

`cached_fm_pair` is the cached font/matrix pair key. It stores a base font pointer, UID/XUID, font type, stable hash, transformation matrix components, cached-character count, xfont lookup state and result, allocator, index in the matrix-pair array, TrueType interpreter state, and design-grid flag. Entries can remain after a restore if they have valid UIDs; free entries are represented by NULL font plus invalid UID.

`fm_pair_cache` manages the array of cached font/matrix pairs with size/max and rover allocation index.

`cached_char` subclasses the general cached-bits header. Its key includes glyph code, font/matrix pair, writing mode, and depth; value fields include bitmap metadata from the common header, xfont glyph id, device width, and offset. The header documents the invariant that every real entry must have either bitmap bits or a valid xfont glyph backed by an xfont.

Cached characters are allocated inside cache chunks, not as standalone GC objects. The header explains that pointers from the cache are traced/relocated when the owning font directory is traced, with special descriptors for cached-char pointers.

`char_cache` stores bitmap-cache common fields, struct/bits allocators, open-addressing hash table, size limits, compression thresholds, and optional glyph marking callback.

`gs_font_dir` is the font directory/cache manager. It owns original/scaled font lists, the font/matrix pair cache, character cache, GC enumeration state, `AlignToPixels`, glyph-to-Unicode data, extension allocator, TrueType interpreter, `GridFitTT`, spot analyzer, and optional global glyph-code callback.

The procedure declarations allocate/init caches, purge selected cached chars, compute character matrices and cache keys, look up/add font/matrix pairs, look up xfonts, purge one pair, and purge a font from character caches.

Filesystem relevance: none. It is in-memory font/glyph cache infrastructure.
