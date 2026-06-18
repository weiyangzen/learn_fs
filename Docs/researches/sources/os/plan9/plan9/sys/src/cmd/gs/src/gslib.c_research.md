# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.c

Standalone Ghostscript library test program. `main` captures real stdio before Ghostscript redefines it, initializes platform and library state, allocates interpreter memory, initializes IO devices, selects/copies the first device, wraps it in a bounding-box device, creates a graphics state, installs a screen halftone, ensures a minimum graphics-state stack, erases the page, dispatches a selected test, outputs the page, prints the bounding box, and finalizes the library.

The file contains test cases covering major public graphics APIs:
- `test1`: randomized kaleidoscope path/color/fill exercise.
- `test2`: bitmap pattern fill over paths.
- `test3`: RasterOp calls on monobit-style devices.
- `test4`: dynamic device resolution through parameter lists.
- `test5`: unmasked, explicit-mask, and chroma-key image APIs.
- `test6`: CIE color rendering, CIEABC color space, and color-mapping wrapper behavior.
- `test7`: non-monotonic Type 5 halftone masks.
- `test8`: partially transparent pixmap patterns.
- optional `test10`: captured printer-output replay under `CAPTURE`.

It also provides local stubs for GC relocation procedures, `gs_to_exit`, `gs_abort`, `copysign`, an ordered-dither spot function, rectangle-fill helper, and deterministic random number generation.

This is not production rendering code; it is a broad integration harness for validating Ghostscript library/device/color/path/image APIs.
