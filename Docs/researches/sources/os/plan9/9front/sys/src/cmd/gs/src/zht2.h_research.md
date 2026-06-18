# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.h

## Purpose
Declares shared Level 2 halftone support used by `zht2.c`.

## Key Functions
- `gs_get_colorname_string()` maps a `gs_separation_name` to a byte string and length.

## Important Behavior
- Includes `gscspace.h` for `gs_separation_name`.
- Guarded by `zht2_INCLUDED`.

## Research Notes
Small cross-file declaration for colorant-name lookup.
