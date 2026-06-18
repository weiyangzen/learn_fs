# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevhit.c

## Role
`gdevhit.c` defines a minimal non-rendering device used for hit detection or insideness testing.

## Behavior
- Exports `gs_hit_detected` as `gs_error_hit_detected`.
- Defines `gs_hit_device`, a tiny 0x0-style device with mostly default or null procs.
- `hit_fill_rectangle` returns `gs_error_hit_detected` whenever asked to fill a rectangle with positive width and height; empty rectangles return success.

## Risks and Notes
- No allocation, file I/O, or external interactions.
- Behavior is intentionally error-driven: painting any real pixels signals a hit.
