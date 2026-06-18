# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/x_.h

Wrapper for including X11 headers in Ghostscript’s X11 driver.

Key points:
- Temporarily undefines Ghostscript’s `private` macro because some X headers use `private` as a member name, then restores it as `private_`.
- Defines `have_Xdebug` for non-VMS builds.
- For VMS GNU C, maps the subset of X/Xt names used by Ghostscript to lowercase names to avoid GNU C’s mixed-case external name transformation.
- For non-GNU VMS, includes `vms_x_fix.h`.
- Includes DECWindows headers on VMS and standard `<X11/...>` headers elsewhere.
- Provides fallback for old X11R3 lacking `XtOffsetOf`.
- Defines `HaveStdCMap` based on `XtSpecificationRelease >= 4`; for older X11, supplies `XVisualIDFromVisual`.
- Defines no-op successful `XInitImage` for pre-X11R6.

Dependencies and interactions:
- Used by Ghostscript X11 device code.
- Works with `vms_x_fix.h` for VMS portability.

Research relevance:
- Central X11 compatibility wrapper across Unix, VMS, and old X11 releases.
