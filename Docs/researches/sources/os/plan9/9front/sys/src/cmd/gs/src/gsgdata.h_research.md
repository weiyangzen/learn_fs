# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.h

## Role

`gsgdata.h` defines the glyph data return structure and lifecycle API for outline/bitmap data requested from fonts.

This is glyph data API infrastructure, not filesystem code.

## Main Types

- `gs_glyph_data_t`
- `gs_glyph_data_procs_t`

`gs_glyph_data_t` stores:

- `gs_const_bytestring bits`
- procedure table
- procedure-private data
- optional memory allocator

## Public API

- `gs_glyph_data_substring`
- `gs_glyph_data_free`
- `gs_glyph_data_from_string`
- `gs_glyph_data_from_bytes`
- `gs_glyph_data_from_null`

## Important Contract

Clients receiving glyph data must call `gs_glyph_data_free` when finished. Implementors should pass a font pointer only when the returned data was newly allocated and should be freed by the client.
