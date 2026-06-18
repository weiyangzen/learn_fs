# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.c

Implements basic Ghostscript path construction, current point handling, clipping, and default clip box computation.

Key functions:
- `gs_newpath`, `gs_closepath`, `gs_upmergepath`, `gx_current_path`.
- `gs_currentpoint`: inverse-transforms device current point to user space.
- `gs_moveto`, `gs_rmoveto`, `gs_lineto`, `gs_rlineto`, `gs_curveto`, `gs_rcurveto`.
- Internal transform compatibility and coordinate clamping helpers.
- `gx_effective_clip_path`: caches effective intersection of clip path and view clip path, with memory-device exception.
- `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`.
- `gx_clip_to_rectangle`, `gx_clip_to_path`, `gx_default_clip_box`.

Integration:
- Uses graphics state internals, fixed-point path API, matrix transforms, clipping path APIs, and device geometry.
- `gx_default_clip_box` respects `ImagingBBox` when set, otherwise derives from media size, hardware margins, and device initial matrix.

Risk notes:
- Relative path operators include comments noting range checks are still “fixme”.
- `gx_effective_clip_path` has complex ownership/shared-state handling; stale IDs or alias mistakes could leak or corrupt clipping.
- Coordinate clamping can mask extreme user-space inputs depending on `clamp_coordinates`.
