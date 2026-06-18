# File Research: sources/os/plan9/9front/sys/src/cmd/image/util.c

Provides shared utility functions for image commands.

Key points:
- `initworkrects` splits a rectangle into horizontal bands for parallel processing.
- `emalloc` and `erealloc` fatal-exit on allocation failure and set malloc/realloc tags.
- `eallocmemimage` allocates and clears a `Memimage`.
- `ereadmemimage` and `ewritememimage` wrap image I/O with fatal errors.
- `eallocimage` wraps display `Image` allocation.
- `memimage2image` creates a display `Image` from a `Memimage` by loading one scanline at a time.

Dependencies and interactions:
- Used by `affinewarp.c`, `correlate.c`, and `histogram.c`.

Research relevance:
- Shared reliability and display-conversion support for Plan 9 image-processing commands.
