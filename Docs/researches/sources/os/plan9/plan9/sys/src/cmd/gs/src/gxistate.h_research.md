# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxistate.h

Ghostscript imager state definition.

Key contents:
- Documents the language-independent subset of PostScript graphics state retained by the imager library.
- Defines opaque color rendering dependencies: halftones, device colors, device halftones.
- Defines `gx_transfer` and macros for color rendering state: halftone, screen phase, device halftone, CIE rendering, black generation, undercolor removal, transfer maps, CIE caches, color mapping procs, DeviceN component map, and pattern cache.
- Defines GC/reference-count pointer enumeration macros for color rendering state.
- Defines `gs_imager_state_common`, including memory/client data, line params, CTM, current point, RasterOp, alpha/blend/transparency/soft-mask fields, text knockout, overprint state, flatness/fill/stroke/curve/shading controls, color map proc hook, and color rendering state.
- Provides CTM access macros and inline accessors for flatness, line params, and logical operation.
- Declares initialization, copy, reference-count, assignment, release, and screen phase APIs.

Notable dependencies:
- Line parameters from `gxline.h`.
- Fixed matrices from `gxmatrix.h`.
- Color, transfer, transparency, and RasterOp headers.

Research notes:
- The CTM is stored as `gs_matrix_fixed`, so callers must use `ctm_only` when an API needs a plain `gs_matrix`.
- `effective_transfer` pointers are relocated specially but not GC-enumerated because they alias objects owned/reference-counted elsewhere.
