# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/Makefile

Builds `libmemdraw.a`, the in-memory raster drawing library.

Key content:
- Includes `../Make.config`.
- Archives image allocation, drawing, shape, font, IO, color-map, and stub hardware-draw objects.
- Does not include test/generator programs such as `drawtest.c`, `arctest.c`, or `mkcmap.c` in the library object list.
