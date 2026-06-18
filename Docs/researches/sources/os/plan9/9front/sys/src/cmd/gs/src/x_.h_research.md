# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/x_.h

Ghostscript wrapper for X11 headers used by the X display driver.

Key points:
- Undefines `private` before including X headers because some X implementations use it as a member name.
- Defines `have_Xdebug` except on VMS.
- For VMS GNU C, maps selected mixed-case X/Xt function names to lowercase forms to match GNU C name transformation behavior.
- For VMS non-GNU paths, includes `vms_x_fix.h`.
- Includes DECWindows headers on VMS and standard `<X11/...>` headers elsewhere.
- Supplies compatibility for older X11:
  - Defines `XtOffsetOf` via `offsetof` or `XtOffset`.
  - Sets `HaveStdCMap` based on `XtSpecificationRelease >= 4`.
  - Provides `XVisualIDFromVisual` fallback for X11R3.
  - Defines `XInitImage(im) 1` before X11R6.
- Restores Ghostscript’s `private` macro as `private_`.

Dependencies and interactions:
- Used by Ghostscript X11 display/device source.
- Interacts with `vms_x_fix.h` for VMS symbol handling.

Research relevance:
- Main X11 portability wrapper, bridging VMS, old X11 releases, and Ghostscript’s internal macro conventions.
