# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.c

## Role

Core Ghostscript font directory, font allocation, scaled-font cache, font state, cache-parameter, purge, and default font/glyph procedure implementation.

## Main Data

Defines default cache size constants for large and small memory systems, `gs_font_procs_default`, GC descriptors for font directories and fonts, original/scaled font lists, character cache integration, and font notification lifecycle.

## Control Flow

Font directories are allocated with character cache limits. Fonts are allocated and minimally initialized with IDs, notification lists, default outline-use policy, and procedure tables. `gs_definefont` registers base fonts. `gs_makefont` multiplies matrices, reuses cached scaled fonts when possible, clones font structures, invokes type-specific make hooks, and manages scaled cache eviction. State helpers set/current/root fonts. Cache parameter functions expose and mutate character cache limits. `gs_purge_font` unlinks fonts and purges related char caches. Default procedures implement basic font info, similarity, notdef detection, dummy glyph methods, and glyph info via outline path accumulation.

## Dependencies

Uses Ghostscript memory, GC, matrix, graphics state, device, font, char cache, path, UID, and notification infrastructure.

## Notes

Base-font list pointers are weak for GC marking but relocated during GC. Composite scaled fonts are deliberately not cached because their makefont hooks mutate descendant font vectors.
