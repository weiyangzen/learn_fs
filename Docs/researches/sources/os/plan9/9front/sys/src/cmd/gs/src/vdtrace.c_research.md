# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.c

Implementation of Ghostscript’s debug-only visual tracing helper.

Key points:
- Defines global trace interface pointers `vd_trace0` and `vd_trace1`, plus a 128-byte `vd_flags` enable table.
- Maintains current scaled point position in private globals `px` and `py`.
- Scales incoming coordinates using interface origin, scale, and shift fields.
- Implements visual path calls: move, line, multi-line, cubic curve, bar, square, rectangle, quadrilateral, curve outline, circle, round marker, and text.
- If a backend lacks `curveto`, `vd_impl_curveto` flattens cubic Beziers into line segments in `DEBUG` builds.
- `vd_setflag` enables/disables trace categories by low 7 bits of a character.
- Most functions no-op immediately if `vd_trace1 == NULL`.

Dependencies and interactions:
- Includes `math_.h`, `gxfixed.h`, and `vdtrace.h`.
- Called through macros in `vdtrace.h` only when `VD_TRACE && DEBUG` is active.
- Backend behavior is supplied by `vd_trace_interface` function pointers.

Research relevance:
- Debug visualization hook for rendering/path internals. It is not part of normal release behavior but can affect debug diagnostics and visual stepping.
