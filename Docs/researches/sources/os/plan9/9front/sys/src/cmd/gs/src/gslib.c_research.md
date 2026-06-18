# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.c

Standalone Ghostscript library test program, despite the nearby initialization header name. It exercises core drawing, device, color, image, halftone, and compositor APIs.

Key behavior:
- Captures real stdio before Ghostscript I/O redirection and initializes platform/library state.
- Allocates interpreter/reference memory, initializes I/O devices, selects a device, wraps it in a bbox device, and creates a `gs_state`.
- Prints device name through the parameter-list API and optionally sets `OutputFile` to `-`.
- Installs a screen halftone using an ordered dither spot function.
- Runs one of several test routines selected by command-line argument, outputs the page, and prints the bounding box.
- Provides GC stubs for relocation and pointer procs because this test harness is not a full interpreter GC environment.
- Provides `gs_to_exit` and `gs_abort` cleanup/exit stubs.

Test routines:
- `test1`: random colored kaleidoscope drawing with transformations and fills.
- `test2`: bitmap pattern fill over a polygon, including colored and uncolored pattern usage.
- `test3`: limited RasterOp exercise against monobit devices.
- `test4`: dynamic device resolution/page parameter update through `gs_putdeviceparams`.
- `test5`: ImageType 1, 3, and 4 image paths, including explicit masks and chroma-key masks.
- `test6`: CIE color rendering, CIEABC color space setup, and color-mapping device modes.
- `test7`: non-monotonic halftone mask construction.
- `test8`: partially transparent indexed pixmap pattern.
- Optional `test10` under `CAPTURE`: replays captured printer output after setting page/device parameters.

Dependencies:
- Pulls in many graphics-library subsystems: state, color spaces, CIE, image parameters, path/paint, RasterOp, devices, bbox device, cmap device, and halftones.

Research notes:
- This file is best understood as a broad integration smoke-test harness for Ghostscript’s C API.
- It is not implementing the `gslib.h` init/fini functions; it calls them.
