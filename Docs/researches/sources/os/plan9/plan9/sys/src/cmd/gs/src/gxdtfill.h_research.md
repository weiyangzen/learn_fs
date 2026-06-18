# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdtfill.h

Configurable include-template implementing trapezoid filling.

- Not a conventional standalone header; intended to be included multiple times with different macro configurations.
- Required configuration macros include:
  - `GX_FILL_TRAPEZOID`
  - `CONTIGUOUS_FILL`
  - `SWAP_AXES`
  - `FILL_DIRECT`
  - `LINEAR_COLOR`
  - `EDGE_TYPE`
  - `FILL_ATTRS`
- Implements scan-conversion for trapezoids bounded by left/right edges and y range.
- Normal mode paints pixels whose centers lie inside the trapezoid, excluding right/top boundaries.
- `CONTIGUOUS_FILL` mode adds minimal extra pixels to avoid dropouts in narrow trapezoids.
- `LINEAR_COLOR` mode fills scanlines with gradient color and returns overflow errors through gradient setup/fill path.
- Uses fixed-point rounding and rational-floor logic to handle edge cases around pixel centers.
- Optimizes vertical-edge rectangle cases when not filling linear color.
- Supports swapped axes by swapping rectangle coordinates at fill time.
- Uses direct device `fill_rectangle` for pure color fast paths when `FILL_DIRECT` is enabled, otherwise goes through device-color fill dispatch.
- Contains debug visualization hooks through `vd_rect`.
- Checks for interrupts before returning.

Role: shared low-level rasterization algorithm generator for multiple trapezoid-fill variants.
