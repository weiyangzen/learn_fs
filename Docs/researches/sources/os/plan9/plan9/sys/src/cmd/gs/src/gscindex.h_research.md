# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscindex.h

## Purpose
Public client interface for Ghostscript Indexed color spaces.

## Key Contents
- Declares `gs_cspace_build_Indexed`.
- Declares palette/introspection helpers:
  - `gs_cspace_indexed_num_entries`,
  - `gs_cspace_indexed_value_array`,
  - `gs_cspace_indexed_set_proc`,
  - `gs_cspace_indexed_lookup`.

## Important Details
- Documents two modes:
  - byte string table supplied by client,
  - procedure-backed palette with cached float values.
- Notes that for byte-table mode, the client owns the table memory and the color space does not free it.
- Notes that procedure-backed Indexed spaces can use the default palette lookup procedures unless the client overrides them.

## Dependencies
Includes `gscspace.h`.

## Research Notes
The implementation is in `gscolor2.c`. The header describes `gs_cspace_indexed_value_array` as exposing the cached value array for procedure-backed Indexed spaces; the implementation appears to return `0` for `use_proc` spaces, which looks inconsistent.
