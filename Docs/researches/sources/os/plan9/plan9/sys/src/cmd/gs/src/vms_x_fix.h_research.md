# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vms_x_fix.h

VMS compatibility header that remaps mixed-case X/Motif/Xt/pthread/system symbols to uppercase external names.

Key points:
- Intended to repair Xlib definitions when compiling on VMS with `/name=(as_is)`.
- Contains a large table of `#define` aliases for Xlib, Motif `Xm*`, Xt, Xrm, Xmu, pthread, `lib$*`, and `sys$*` names.
- Includes widget class object aliases such as `topLevelShellWidgetClass`, `xmTextWidgetClass`, and many Motif class records.
- Declares `extern void XtFree(char*)` with C++ linkage protection at the end.
- Does not implement behavior; it only changes symbol spelling before headers/linkage.

Dependencies and interactions:
- Included from `x_.h` for non-GNU VMS builds.
- Addresses VMS linker/case behavior for external symbols in X-related drivers.

Research relevance:
- Large portability shim for historical VMS X11/Motif support.
