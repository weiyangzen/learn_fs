# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht1.c

## Purpose
Implements `setcolorscreen`, the Level 1 color halftone screen operator.

## Key Functions
- `zsetcolorscreen()` parses four screen definitions, prepares a color halftone, and schedules sampling for each component.
- `setcolorscreen_finish()` installs the completed color screen and records component procedures.
- `setcolorscreen_cleanup()` frees temporary halftone structures.

## Important Behavior
- Four component screens are parsed from red, green, blue, and gray frequency/angle/procedure triples.
- Uses a dummy C spot function until the PostScript spot procedures are sampled.
- Component indices are shuffled to match device component order.
- Temporary `gs_halftone` and `gx_device_halftone` allocations are cleaned up after installation.

## Research Notes
Layered on the sampling helper from `zht.c`.
