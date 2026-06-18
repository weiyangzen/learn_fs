# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsel.h

## Role

`gscsel.h` defines color operand selection values used to distinguish source and texture colors for RasterOp and related graphics-state operations.

This is rendering state infrastructure, not filesystem code.

## Main Definitions

`gs_color_select_t` values:

- `gs_color_select_all = -1`
- `gs_color_select_texture = 0`
- `gs_color_select_source = 1`

Also defines `gs_color_select_count` as `2`.

## Important Contract

`gs_color_select_texture` is explicitly zero because it is used for `currenthtphase`.

## Notable Risks

Changing numeric values would break callers that rely on the documented zero and count semantics.
