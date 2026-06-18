# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwtrace.c

## Role
Win32 graphical trace server for Ghostscript visual debugging, implementing `vd_trace_interface` callbacks with GDI drawing into an image/tracer window.

## Contents
- Defines `vd_trace_host_s` holding initialization state, tracer `IMAGE`, HDC nesting count, window height, line width, current color, selected pen/brush objects, and last move point.
- Lazily creates a tracer window using `image_new(NULL, NULL)` and `image_open`.
- Converts RGB integers to Windows `COLORREF`.
- Provides coordinate conversion with Y-axis inversion based on current window height.
- Manages HDC acquisition/release with nested `get_dc`/`release_dc` counting and pen/brush selection/deletion.
- Implements trace drawing callbacks for erase, begin/end path, move, line, Bezier curve, close path, circle, filled round marker, fill, stroke, set color, set line width, text, and placeholder wait.
- Reads optional scale/shift/origin adjustments from `gs_vdtrace.ini`.
- `visual_tracer_init` installs callbacks into global `visual_tracer`; `visual_tracer_close` deletes/closes the tracer image.

## Important Interfaces
- Global `vd_trace_interface visual_tracer`.
- `visual_tracer_init`.
- `visual_tracer_close`.

## Dependencies And Coupling
- Includes `dwimg.h` before Ghostscript headers to avoid `RGB` macro conflicts.
- Uses `vdtrace.h`, `gsdll.h`, `gscdefs.h`, and local `dwtrace.h`.
- Reuses image-window infrastructure from `dwimg.c`; tracer windows are identified by `device == NULL`.

## Risks And Notes
- Comment states WM_PAINT restoration is not implemented, so trace drawings may not repaint after exposure.
- `dw_gt_erase` passes raw `rgbcolor` to `CreateSolidBrush` rather than using `WindowsColor`, unlike pen/brush creation elsewhere.
- Several callbacks call `get_window` but then assume an HDC is already active; callers must respect the trace interface get/release protocol.
- Uses `private` macro from Ghostscript headers after include ordering.

## Filesystem Relevance
None, except reading trace settings from an INI file.
