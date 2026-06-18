# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.h

## Role

`gsfcmap.h` is the public interface to Ghostscript CMaps.

## API

Declares:

- `gs_cmap_create_identity`
- `gs_cmap_create_char_identity`
- `gs_cmap_decode_next`
- `gs_cmap_ToUnicode_alloc`
- `gs_cmap_ToUnicode_add_pair`

`gs_cmap_decode_next` decodes from a string, updates the index, returns 0 for CID/name mappings, positive byte count for character-code mappings, and sets `gs_no_glyph` for undefined characters.

## Types

Forward-declares abstract `gs_cmap_t`.

## Dependencies

Includes `gsccode.h` for character/glyph code types and expects `gs_memory_t`, `gs_const_string`, `gs_char`, and `gs_glyph`.

## Integration Notes

This is the stable client-level surface; detailed CMap representations and enumeration APIs live in internal headers such as `gxfcmap.h`.

## Risks

The public decode contract requires callers to handle both glyph output and positive return-code character mappings. Ignoring positive returns can misinterpret ToUnicode/character-map cases.
