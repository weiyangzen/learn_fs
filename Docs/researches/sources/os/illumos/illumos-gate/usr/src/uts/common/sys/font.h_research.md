# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/font.h

This header defines console font data structures and rendering conversion interfaces.

Font maps:
- `enum vfnt_map` distinguishes normal, normal right-hand, bold, bold right-hand, and map count.
- `font_map` maps source glyphs to target glyph ranges.
- `font_info` is a fixed-size boot-passed summary containing checksum, dimensions, bitmap size, and per-map counts.

In-memory font structures:
- `struct font` holds four mapping tables, bitmap bytes, glyph width/height, and map counts.
- `bitmap_data_t` describes bitmap dimensions, compressed/uncompressed size, compressed data pointer, and associated `struct font`.
- `FONT_FLAGS` indicates whether a font was auto-loaded, manually loaded, passed by bootloader, built in, or marked for reload.
- `struct fontlist` stores a named font, flag, data pointer, loader callback, and STAILQ linkage.

File format:
- `FONT_HEADER_MAGIC` is `"VFNT0002"`.
- `struct font_header` is packed and contains magic, glyph dimensions, glyph count, and four map counts.

Globals and defaults:
- `fonts` is the global font list.
- SPARC defaults to `font_data_12x22`; other platforms default to `font_data_8x16`.
- `BORDER_PIXELS` defines console border spacing.

Functions:
- Reset font flags, select a font, look up a glyph, and convert font bitmap data to 4/8/16/24/32-bit pixel buffers.

Dependencies and relationships:
- Used by console/framebuffer code and boot handoff paths.
- The bootloader-passed format avoids pointer-size assumptions by copying fixed-size metadata and byte arrays.
