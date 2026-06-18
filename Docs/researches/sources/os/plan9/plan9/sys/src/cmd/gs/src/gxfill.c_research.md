# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.c

## Purpose
Implements Ghostscript's core path filling algorithm: a topological spot decomposition with trapezoid and scanline backends, clipping integration, fill adjustment, shading optimization, spot analyzer support, and character dropout prevention.

## Public Entry Points
- `gx_adjust_if_empty`: expands nearly empty boxes so zero-width/epsilon-width fills can still mark pixels.
- `gx_default_fill_path`: default device `fill_path` implementation, with a special path for pattern/shading fills.
- Internal main routine `gx_general_fill_path`: orchestrates bounding, clipping, flattening, active-line construction, backend selection, and cleanup.

## Fill Pipeline
1. Compute path bounding box before flattening.
2. Decide whether pseudo-rasterization is needed for small character fills.
3. Check inner/outer clipping boxes and optionally wrap the target with a clip device.
4. Normalize fill adjustment fields for center-of-pixel and any-part-of-pixel behavior.
5. Flatten/copy/reduce path when needed, optionally merging contacting contours for large paths.
6. Build a Y-sorted active-line list from subpaths/segments/curves.
7. Select trapezoid or scanline filling backend.
8. Run the backend with banding constraints.
9. Release temporary path, active-line, margin, and section storage.

## Active-Line System
- `active_line` records a monotonic line/flattened curve piece, its current/next X, direction, iterator state, and linked-list position.
- `x_order`, `insert_y_line`, `insert_x_new`, `move_al_by_y`, `resort_x_line`, and `intersect_al` maintain Y and X ordering and handle segment crossings.
- Non-monotonic curves are split through `gx_flattened_iterator` and contour scanning logic.

## Backend Selection
- Trapezoid backend is preferred for pseudo-rasterization, non-curved paths, flat paths, and spot analyzer devices.
- Scanline backend is used where avoiding double writes matters, especially with non-idempotent RasterOps and fill adjustment.
- Rectangular non-idempotent fills can bypass the general algorithm and call rectangle ROP fill directly.
- Pattern 2 shading fills invert subdivision order: clip first, then let shading fill use the path intersection.

## Generated Template Use
Includes:
- `gxfillts.h` twice for direct/non-direct slanted trapezoid adjustment helpers.
- `gxfilltr.h` seven times for spot analyzer, pseudo-rasterization direct/non-direct, adjusted direct/non-direct, and unadjusted direct/non-direct trapezoid loops.
- `gxfillsl.h` twice for direct/non-direct scanline loops.

## Range List Support
The scanline backend uses `coord_range_list_t` to merge integer X ranges within a sampled Y pixel band, minimizing overdraw while preserving fill/eofill behavior.

## Dependencies
Depends on path, clipping, device, color, halftone tile, imager state, pattern, spot analyzer, dropout prevention, and fixed-point math headers.

## Notable Risks / Edge Cases
The implementation is arithmetic-heavy and has many comments about numerical corner cases: line intersections, triple intersections, non-monotonic curves, horizontal curve pieces, band boundaries, and fixed-point overflow. The pseudo-rasterization path is deliberately specialized for character sizes below a fixed threshold.
