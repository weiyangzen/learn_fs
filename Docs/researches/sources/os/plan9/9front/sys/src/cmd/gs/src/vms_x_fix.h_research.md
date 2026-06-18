# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vms_x_fix.h

VMS compatibility header that remaps X11/Motif/Xt/pthread/VMS routine names to uppercase linker symbols.

Key points:
- Guarded by `vms_x_fix_INCLUDED`.
- Intended to repair Xlib definitions when compiling on VMS with `/name=(as_is)`.
- Defines hundreds of macros mapping mixed/lowercase APIs to uppercase names, including:
  - Xlib and X extension functions (`XOpenDisplay`, `XDrawLine`, `XPutImage`, etc.).
  - Motif `Xm*` functions and widget classes.
  - Xt toolkit functions and widget classes.
  - X resource manager functions.
  - selected private `_Xm*` and `_Xt*` symbols.
  - VMS `lib$*` and `sys$*` routines.
  - pthread APIs to uppercase VMS symbols.
- Contains a duplicate `XrmStringToQuark` mapping.
- Declares `extern void XtFree(char*)` inside `extern "C"` guards.

Dependencies and interactions:
- Included by `x_.h` for VMS non-GNU compiler paths before DECWindows headers.
- Exists solely for VMS name-mangling/link compatibility.

Research relevance:
- Large portability shim for building Ghostscript’s X11 display driver on VMS. It has no runtime logic but heavily affects symbol resolution on that platform.
