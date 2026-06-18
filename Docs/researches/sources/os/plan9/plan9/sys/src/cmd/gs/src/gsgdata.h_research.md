# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.h

## Role

Client and implementor interface for scalable glyph outline data access.

## Main Data

Defines `gs_glyph_data_t`, containing a constant bytestring, procedure table, procedure data, and memory allocator. Defines `gs_glyph_data_procs_t` with `free` and `substring` hooks.

## Main API

Declares `gs_glyph_data_substring`, `gs_glyph_data_free`, `gs_glyph_data_from_string`, `gs_glyph_data_from_bytes`, and `gs_glyph_data_from_null`.

## Contract

Clients receiving glyph data must call `gs_glyph_data_free` when finished. Implementors pass `NULL` as font for data retained elsewhere and the font pointer for data newly allocated for the client.

## Dependencies

Uses Ghostscript structure descriptors, bytestrings, memory, and font forward declarations.
