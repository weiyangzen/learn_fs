# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.h

Public interface and macros for visual tracing.

Key points:
- Defines `vd_trace_interface` callback table with size queries, DC acquire/release, erase, path construction, drawing primitives, fill/stroke, color/line width, text, wait, and transform update callbacks.
- Declares `vd_trace0`, `vd_trace1`, `vd_flags`, and implementation functions from `vdtrace.c`.
- Defines `RGB(r,g,b)` fallback.
- When `VD_TRACE && DEBUG`, macros conditionally acquire a trace context based on `vd_flags`, emit scaled drawing primitives, query size/scale/origin, and save/restore/disable tracing.
- When not tracing or not DEBUG, all tracing macros become `DO_NOTHING`/constants.
- Comments define the painting contract: acquire with `vd_get_dc`, draw, release with `vd_release_dc`; some primitives paint immediately while path primitives may require fill/stroke.

Dependencies and interactions:
- Requires Ghostscript macros such as `BEGIN`, `END`, `DO_NOTHING`, and `false` from surrounding headers.
- Used by graphics debugging code and optionally by Windows tracing integration.

Research relevance:
- Important for understanding debug-only instrumentation boundaries and why trace calls should be side-effect free in release builds.
