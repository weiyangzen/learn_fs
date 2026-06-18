# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.h

Defines the client interface for PatternType 1 tiling patterns.

Key definitions:
- `gs_pattern1_template_t`: common pattern template plus `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, and `PaintProc`.
- `gs_client_pattern` backward-compatible typedef.
- PatternType 1 GC descriptor macro.

Exports:
- `gs_cspace_build_Pattern1`
- `gs_pattern1_init`
- `gs_makepattern`
- `gs_getpattern`
- `gs_makepixmappattern`
- `gs_makebitmappattern_xform`
- `gs_makebitmappattern` compatibility macro.

Integration:
- Includes `gspcolor.h` and `gxbitmap.h`.
- Used by clients that create colored/uncolored tiling patterns or PCL-style bitmap/pixmap patterns.

Risk notes:
- Header comments make bitmap-data lifetime explicit: raw image data must outlive the pattern.
- Mask patterns require 1-bit depth; colored pixmap patterns require Indexed color space.
