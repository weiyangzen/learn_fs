# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpcolor.c

## Purpose
Implements Level 2 Pattern color-space support, tiling pattern construction, pattern cache initialization, and deferred pattern painting.

## Key Functions
- `zpcolor_init()` creates the graphics-state pattern cache.
- `int_pattern_alloc()` creates interpreter pattern client data.
- `zbuildpattern1()` builds tiling pattern instances from pattern dictionaries and matrices.
- `zsetpatternspace()` installs Pattern color spaces with optional base color space.
- `zPaintProc()` triggers deferred PaintProc execution through `e_RemapColor`.
- `pattern_paint_prepare()`, `pattern_paint_finish()`, and `pattern_paint_cleanup()` manage rendering a pattern tile and caching it.

## Important Behavior
- `zbuildpattern1` validates `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, `PaintProc`, and optional UID.
- Uncolored Pattern space captures the current non-pattern color space as its base.
- Pattern painting saves/restores graphics state and may use an internal accumulator device or device-managed accumulation.
- PaintProc stack leftovers are cleaned up after rendering.
- Pattern cache entries are added after successful tile rendering.

## Research Notes
Complex rendering callback path bridging PostScript PaintProc execution to Ghostscript pattern caching.
