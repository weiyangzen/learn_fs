# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpcolor.c

LanguageLevel 2 Pattern color support for tiling patterns. It registers `.buildpattern1`, `.setpatternspace`, and internal pattern-paint continuations.

`zpcolor_init` allocates the pattern cache in system memory and attaches it to the graphics state. `zbuildpattern1` reads a pattern dictionary and matrix, validates `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, `PaintProc`, and optional UID, allocates an `int_pattern` carrying the original dictionary, and creates a pattern instance through `gs_makepattern`.

`zsetpatternspace` installs a Pattern color space, optionally using the current non-Pattern color space as the base space for uncolored patterns, and resets the interpreter’s current pattern object to null.

Pattern rendering is asynchronous. `zPaintProc` requests an `e_RemapColor` callback. `pattern_paint_prepare` creates or delegates pattern accumulation, saves/restores graphics state around the pattern’s saved state, switches to the accumulator or external accumulation path, pushes cleanup state, and schedules the user `PaintProc`. `pattern_paint_finish` adds the rendered tile to the pattern cache and removes PaintProc stack junk. `pattern_paint_cleanup` closes the accumulator, grestores, and notifies devices when external accumulation completes.
