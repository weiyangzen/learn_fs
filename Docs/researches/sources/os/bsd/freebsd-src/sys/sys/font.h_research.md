# File Research: sources/os/bsd/freebsd-src/sys/sys/font.h

## Purpose
Defines VT font metadata, Unicode-to-glyph mapping structures, bitmap data, and packed on-disk/in-memory VFNT headers.

## Main Interfaces
- `enum vfnt_map_type`: normal, normal-right, bold, bold-right maps.
- `struct font_info`: checksum, dimensions, bitmap size, map counts.
- Packed `struct vfnt_map`: source codepoint, destination glyph, run length.
- `struct vt_font`: map pointers, bitmap bytes, dimensions, map counts, refcount.
- `vt_font_bitmap_data_t`: compressed/uncompressed bitmap package and loaded font pointer.
- `FONT_FLAGS`: auto, manual, builtin, reload.
- `struct fontlist` and `font_list_t`.
- `FONT_HEADER_MAGIC` and packed `struct font_header`.

## Dependencies And Integration
Uses queue macros. The comments specify binary-search lookup over sorted maps and fallback behavior from bold to normal glyphs and missing glyphs to glyph 0.

## Risk Notes
Packed structures and magic string define VFNT file format compatibility. Map ordering is an implicit correctness requirement for lookup performance and behavior.
