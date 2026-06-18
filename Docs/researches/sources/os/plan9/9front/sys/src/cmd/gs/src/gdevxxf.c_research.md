# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxxf.c

Ghostscript X11 external-font implementation. It lets the X11 display device substitute suitable X server fonts for Ghostscript fonts.

Key behavior:
- Exposes `gdev_x_get_xfont_procs` with lookup, glyph conversion, metrics, render, and release callbacks.
- Maps PostScript font names to configured X11 font names, choosing Adobe-fontspecific or ISO8859-1 encodings and fixed/scalable X font instances.
- Accepts only simple non-skewed transforms: upright, mirrored, or 90-degree rotations when font extensions are enabled.
- Rejects too-small and too-large X fonts to avoid bad metrics or server lockups.
- Converts Ghostscript character codes across StandardEncoding and ISO encodings when needed.
- Renders directly to an unbuffered X11 device with batched `XTextItem`s, or rasterizes into a 1-bit X pixmap and copies bits to other devices.

Notable dependencies:
- X11 APIs and Ghostscript X device structures from `x_.h`, `gdevx.h`, and `gxxfont.h`.
- Uses configured `x11fontmap` lists from the X device.

Research notes:
- The file is display/font acceleration code, not filesystem logic.
- `x_release` intentionally does not free the X font because the device may not be open reliably at release time.
