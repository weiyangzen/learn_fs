# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.h

This header declares the public CMap API.

Declared functions:
- `gs_cmap_create_identity`
- `gs_cmap_create_char_identity`
- `gs_cmap_decode_next`
- `gs_cmap_ToUnicode_alloc`
- `gs_cmap_ToUnicode_add_pair`

The decode contract:
- Returns `0` for CID/name mappings.
- Returns positive `N` for character-code mappings where `N` is the number of bytes.
- Returns an error on failure.
- Updates the input index and writes font index, character code, and glyph.
- Undefined characters set `*pglyph = gs_no_glyph`.

It forward-declares abstract `gs_cmap_t` and includes `gsccode.h` for character/glyph code definitions.
