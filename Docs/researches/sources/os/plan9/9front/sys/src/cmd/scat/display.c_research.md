# File Research: sources/os/plan9/9front/sys/src/cmd/scat/display.c

Purpose: Sends generated DSS pictures or Plan 9 draw images to `/bin/page -w` for display.

Key routines:
- `displaypic`: forks page, writes a raw `k8` image header plus `Picture` bytes through a pipe, frees page-aligned segments with `segfree` as data is handed off, and frees the `Picture`.
- `displayimage`: forks page, writes a Plan 9 image using `writeimage`, then frees it.

Integration: Used by `image.c`/`scat.c` for DSS plate display and by `plot.c` for generated sky maps.

Risks:
- Relies on Plan 9 image pipe formats and `/bin/page`.
- Child process inherits a narrowed file descriptor group through `rfork`.
- `displaypic` has careful memory release behavior for large image buffers.
