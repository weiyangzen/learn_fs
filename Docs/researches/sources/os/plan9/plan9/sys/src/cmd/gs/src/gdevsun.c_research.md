# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsun.c

Purpose: Ghostscript display driver for SunView windows.

Key behavior:
- Defines `sunview`, a display device sized like paper at default 75 dpi.
- Creates a SunView frame and canvas, optionally requesting 24-bit color support.
- Detects monochrome, 8-bit pseudo-color, and true-color display depths and installs matching Ghostscript color info.
- For pseudo-color, allocates a private colormap with black/white plus a preallocated RGB cube, then dynamically allocates exact colors until the map fills.
- For true-color, encodes RGB components directly into the color index.
- Prevents user window close through a destroy hook.
- Implements sync, close, RGB color mapping, reverse color mapping, rectangle fill, mono bitmap stencil copy, color bitmap copy, and line draw.
- On little-endian systems, reverses mono bitmap bit order before Sun pixrect stencil operations and restores it after drawing.

Important dependencies:
- SunView/SunWindows APIs: `suntool/sunview.h`, `suntool/canvas.h`, `sunwindow/cms_mono.h`.
- Ghostscript device API and pixrect memory operations.

Notable risks / findings:
- `sun_copy_mono` intentionally casts away const and mutates caller-provided bitmap data temporarily.
- Comments warn pseudo-color fallback can loop forever if Ghostscript requests colors outside the preallocated cube after the colormap is full.
- The `#endif ./* FAKE_TRUE_COLOR */` directive has unusual trailing tokens.
