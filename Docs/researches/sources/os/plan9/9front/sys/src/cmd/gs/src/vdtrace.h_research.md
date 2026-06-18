# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.h

Interface and macro layer for Ghostscript visual tracing.

Key points:
- Defines `vd_trace_interface`, a backend callback table with scale/origin/shift state and drawing operations.
- Declares global tracing pointers `vd_trace0`, `vd_trace1`, and flag table `vd_flags`.
- Declares implementation helpers from `vdtrace.c`.
- Defines `RGB(r,g,b)` if absent.
- When `VD_TRACE && DEBUG`, macros acquire/release a drawing context, query scale/size/origin, set scale/origin/shift, erase, build paths, draw primitives, fill/stroke, set color/line width, draw text, wait, save/restore, and disable tracing.
- When tracing is disabled or not a debug build, all drawing macros compile to no-ops and simple constants.
- The documented contract requires `vd_get_dc`, drawing calls, then `vd_release_dc`.

Dependencies and interactions:
- Requires Ghostscript macro conventions such as `BEGIN`, `END`, and `DO_NOTHING` from surrounding headers.
- Used by debug-capable modules, including Windows display/debug code.

Research relevance:
- Provides a zero-cost-in-release visual debugging abstraction over path and rendering behavior.
