# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.h

Declares the shared Ghostscript framework for devices that emit high-level/vector drawing commands rather than pure raster output.

Key behavior:
- Documents the intent of “vector” devices: output command streams such as PDF, PostScript, PCL XL, HP-GL/2, CGM, Windows Metafile, or PICT, while still possibly handling text and raster images.
- Defines output filename and dash-pattern limits.
- Defines `gx_path_type_t` flags for fill/stroke/clip, winding/even-odd rule, path optimization, and always-close behavior.
- Defines `gx_rect_direction_t` for rectangle path ordering.
- Defines `gx_device_vector_procs`, the callback table for page begin, graphics-state changes, color changes, path emission, and rectangle/path default hooks.
- Declares default callback implementations `gdev_vector_setflat`, `gdev_vector_dopath`, and `gdev_vector_dorect`.
- Defines `gx_device_vector_common`, extending a device with memory, vector callbacks, output file/stream state, cached imager state, dash cache, saved high-level colors, clipping IDs, fill/stroke options, coordinate scale, page state, optional bbox device, and cached black/white colors.
- Provides initial values and GC descriptor macros for vector devices.
- Declares file/stream opening options for ASCII, sequential output, sequential fallback, and bbox tracking.
- Declares state update helpers for log-op, fill color, fill preparation, stroke preparation, stroke scaling, path writing, polygon/rectangle writing, clip-path writing/updating, and file close.
- Defines common image-enumerator fields and declares begin/end image helpers.
- Declares default device procedures for `OutputFile` parameters and common fill/stroke geometry operations.

Dependencies:
- Includes `gp.h`, `gsropt.h`, `gxdevice.h`, `gdevbbox.h`, `gxiparam.h`, `gxistate.h`, `gxhldevc.h`, and `stream.h`.

Research notes:
- The header is the contract concrete vector devices implement; procedure comments specify which callbacks each helper may invoke.
- The embedded state cache is central to avoiding redundant commands in generated vector output.
