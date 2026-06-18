# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwtrace.c

Purpose: Win32 graphical trace server for Ghostscript’s visual tracing interface.

Major responsibilities:
- Lazily creates a trace `IMAGE` window.
- Provides `vd_trace_interface` callbacks that draw with Win32 GDI.
- Maps Ghostscript trace coordinates to window coordinates.
- Manages an HDC, selected pen/brush, color, line width, and nested `get_dc`/`release_dc` calls.
- Reads optional trace scale/shift/origin settings from `gs_vdtrace.ini`.

Key callbacks:
- Window/device context: `get_size_x`, `get_size_y`, `get_dc`, `release_dc`, `erase`.
- Path construction/drawing: `beg_path`, `end_path`, `moveto`, `lineto`, `curveto`, `closepath`, `fill`, `stroke`.
- Markers/text: `circle`, `round`, `text`.
- Style/settings: `setcolor`, `setlinewidth`, `set_scale`, `set_shift`, `set_origin`.
- `wait` is intentionally not implemented.
- `visual_tracer_init` installs callbacks; `visual_tracer_close` destroys the trace image.

Notes:
- Comments say WM_PAINT image restoration is not implemented.
- Non-Win32 callback macro sets callbacks to zero.
- `dw_gt_erase` passes `rgbcolor` directly to `CreateSolidBrush` instead of converting through `WindowsColor`, unlike pen/brush color setup.

Filesystem relevance: None.
