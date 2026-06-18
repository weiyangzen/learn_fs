# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zrop.c

## Purpose
Implements RasterOp and transparency control operators.

## Key Functions
- `zsetrasterop()` and `zcurrentrasterop()` set/query the current 8-bit raster operation.
- `zsetsourcetransparent()` and `zcurrentsourcetransparent()` set/query source transparency.
- `zsettexturetransparent()` and `zcurrenttexturetransparent()` set/query texture transparency.

## Important Behavior
- RasterOp is validated as an integer up to `0xff`.
- Transparency operators require boolean operands.
- All state changes are delegated to `gsrop` graphics-state APIs.

## Research Notes
Small extension surface for raster operation state.
