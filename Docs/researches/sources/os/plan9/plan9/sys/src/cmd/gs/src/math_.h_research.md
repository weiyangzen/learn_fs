# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/math_.h

`math_.h` is Ghostscript's portable wrapper for `<math.h>`. It includes `std.h`, then either `vmsmath.h` for GNU VAX/VMS or the system math header.

It ensures `M_PI` exists, defines degree/radian conversion constants, and supplies an exact `MAX_FLOAT` expression for IEEE and VAX float formats. It also handles missing or undeclared `hypot` cases, including `_hypot` on MSVC and a `sqrt(x*x+y*y)` fallback on selected older systems.

For debugging, it declares `gs_sqrt` and redefines `sqrt(x)` to include file/line information under `DEBUG`. The header is a portability shim with numerically important constants and debug instrumentation.
