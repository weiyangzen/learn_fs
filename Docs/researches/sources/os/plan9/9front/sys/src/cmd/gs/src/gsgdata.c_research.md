# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.c

## Role

`gsgdata.c` implements `gs_glyph_data_t` lifecycle and substring support for glyph outline/bitmap data returned by font procedures.

This is glyph data management infrastructure, not filesystem code.

## Main Interfaces

- `gs_glyph_data_substring`
- `gs_glyph_data_free`
- `gs_glyph_data_from_string`
- `gs_glyph_data_from_bytes`
- `gs_glyph_data_from_null`

## Core Behavior

Glyph data can be backed by:

- permanent font-owned data, which is not freed
- dynamically allocated string data owned by a font allocator
- byte-string object data, where substringing adjusts offsets without resizing

`gs_glyph_data_free` calls the selected free proc and then resets the glyph data to null, making repeated frees harmless.

## GC Support

The descriptor enumerates/relocates the data byte string and `proc_data`.

## Notable Risks

- `glyph_data_substring_by_font` breaks constness to resize/memmove allocated string data.
- Correct ownership depends on the implementor passing a non-null font only for data allocated for this request and safe to free later.
