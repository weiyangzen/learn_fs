# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.c

Implements basic Ghostscript path construction and clipping routines.

Main behavior:
- Path lifecycle: `gs_newpath`, `gs_closepath`, `gs_upmergepath`, `gx_current_path`.
- Point/line/curve construction: `gs_moveto`, `gs_rmoveto`, `gs_lineto`, `gs_rlineto`, `gs_curveto`, `gs_rcurveto`.
- Coordinate transformation from user space through CTM into fixed device coordinates.
- Coordinate clamping/limit checking through `clamp_point_aux`.
- Current point tracking and subpath start tracking.
- Clipping: `gx_effective_clip_path`, `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`, `gx_clip_to_rectangle`, `gx_clip_to_path`, `gx_default_clip_box`.

Important design:
- Effective clip path is cached by clip/view-clip IDs.
- View clipping is ignored for memory devices, primarily to support cache-device behavior.
- Default clipping box is derived from `ImagingBBox` if present, otherwise media size, hardware margins, and device initial matrix.
