# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxistate.h

Ghostscript imager state definition.

Key contents:
- Documents the subset of PostScript graphics state retained by the language-independent imager library.
- Defines opaque color rendering state dependencies: halftones, device colors, device halftones.
- Defines `gx_transfer` and macros for the color rendering state: halftone, screen phase, device halftone, CIE rendering, black generation, undercolor removal, transfer maps, CIE joint caches, color map procs, DeviceN component map, and pattern cache.
- Defines GC/reference-count pointer enumeration macros for color rendering state.
- Defines `gs_imager_state_common`, including memory, client data, line parameters, CTM, current point, RasterOp, alpha/blend/transparency/soft-mask fields, text knockout, overprint settings, flatness/fill/stroke/curve/shading controls, color map proc hook, and color rendering state.
- Provides CTM access macros and inline accessors for flatness, line params, and logical operation.
- Declares initialization, copy, reference-count, assignment, release, and screen phase APIs.

Notable dependencies:
- Line parameters from `gxline.h`.
- Fixed matrices from `gxmatrix.h`.
- Color, transfer, transparency, and RasterOp headers.

Research notes:
- The CTM is stored as `gs_matrix_fixed`, so callers must use `ctm_only` when APIs require a plain `gs_matrix`.
- Effective transfer pointers are relocated specially but not enumerated for GC because they alias owned/reference-counted objects elsewhere.
