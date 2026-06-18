# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.c

Implementation of Ghostscript’s visual tracer service.

Key points:
- Defines global trace interfaces `vd_trace0`, `vd_trace1`, and `vd_flags[128]`.
- Maintains current scaled point state in private `px`, `py`.
- Provides scale helpers from source coordinates to trace display coordinates using origin, scale, and shift fields.
- Implements drawing wrappers: move, line, multi-line, curve, bar, square, rectangle, quadrilateral, curve stroke, circle, round marker, and text.
- If the trace interface lacks a `curveto` callback, DEBUG builds flatten Beziers into line segments using a second-derivative estimate and `hypot`, `ceil`, `sqrt`.
- `vd_setflag` toggles per-character tracing flags.

Dependencies and interactions:
- Includes `math_.h`, `gxfixed.h`, and `vdtrace.h`.
- Called only through macros in `vdtrace.h`; most calls are compiled out outside DEBUG/VD_TRACE.

Research relevance:
- Diagnostic-only visualization hook for graphics/path debugging; no normal rendering semantics should depend on it.
