# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage2.c

## Purpose
Provides a helper for processing image descriptions that have no explicit source data.

## Key Functions
- `process_non_source_image()` starts a typed image with `gs_image_begin_typed()` and returns the result.

## Important Behavior
- Intended for use by DPS-related code.
- Does not allocate or clean up data-source state because no data is supplied.
- Contains an inline comment noting the hard-coded `uses_color` argument is questionable.

## Research Notes
Small shared helper, not an operator table itself.
