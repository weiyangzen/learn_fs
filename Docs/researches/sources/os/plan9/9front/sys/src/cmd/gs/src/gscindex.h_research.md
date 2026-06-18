# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscindex.h

## Role

`gscindex.h` declares the client API for Ghostscript Indexed color spaces.

This is rendering/color-space infrastructure, not filesystem code.

## Public API

- `gs_cspace_build_Indexed`
- `gs_cspace_indexed_num_entries`
- `gs_cspace_indexed_value_array`
- `gs_cspace_indexed_set_proc`
- `gs_cspace_indexed_lookup`

## Behavior Contract

The header documents two Indexed color modes:

- byte-string lookup table supplied by the client
- procedure-backed palette/cache where clients can fill values directly and optionally replace the lookup procedure

The table memory is owned by the client for string-table color spaces; the color space does not free it.

## Dependencies

Includes `gscspace.h` for color-space definitions and `gs_indexed_params`.

## Notable Risks

- API ownership is mixed: byte lookup tables are external, while procedure-backed maps are allocated by the color-space implementation.
- The corresponding implementation’s `gs_cspace_indexed_value_array` condition appears inconsistent with this header’s procedure-backed palette-accessor description.
