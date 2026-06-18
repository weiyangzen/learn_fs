# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht.h

Public interface for basic Type 1 and color halftone functionality.

Defines:
- `gs_screen_halftone`: frequency, angle, spot function, actual frequency, and actual angle.
- `gs_colorscreen_halftone`: four screen definitions addressable by index or named red/green/blue/gray fields.
- `gs_setscreen`, `gs_currentscreen`, and `gs_currentscreenlevels`.
- `gs_screen_enum` opaque enumeration API for client-driven screen sampling.

The enumerator API lets callers allocate/init a screen, repeatedly ask for a sampling point, provide the spot-function value, and optionally install the completed screen.

This header is intentionally small and exposes only the public procedural layer; implementation and internal order details live in `gsht.c`, `gshtscr.c`, and internal headers.
