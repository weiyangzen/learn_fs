# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.c

## Purpose
Constructs and validates PDF/PostScript shading objects and provides the shared path/clip/background wrapper used to render shadings through type-specific rectangle fill callbacks.

## Public Surface
- Parameter initializers: `gs_shading_Fb_params_init`, `gs_shading_A_params_init`, `gs_shading_R_params_init`, `gs_shading_FfGt_params_init`, `gs_shading_LfGt_params_init`, `gs_shading_Cp_params_init`, `gs_shading_Tpp_params_init`.
- Constructors: `gs_shading_Fb_init`, `gs_shading_A_init`, `gs_shading_R_init`, `gs_shading_FfGt_init`, `gs_shading_LfGt_init`, `gs_shading_Cp_init`, `gs_shading_Tpp_init`.
- Rendering entry: `gs_shading_fill_path_adjusted(...)`.

## Validation and Initialization
- `check_CBFD` validates color-space component count, BBox ordering, and optional function arity against expected domain dimension and color components.
- `check_mesh` validates mesh data sources. Stream/bit-data sources require accepted coordinate/component bit widths; array data sources bypass bit-depth validation.
- `check_BPF` normalizes array data sources to 2-bit flags and validates stream flag widths of 2, 4, or 8 bits.
- Function-based shading requires an invertible matrix.
- Radial shading rejects equal domain bounds and negative radii.
- Free-form mesh rejects equal coordinate decode bounds when decode is present.
- Lattice mesh requires `VerticesPerRow >= 2`.

## Allocation and GC
- Uses `ALLOC_SHADING` to allocate the concrete shading, set type/procs, copy params, and return a generic `gs_shading_t`.
- Defines GC descriptors for generic and mesh shadings. Mesh GC enumeration relocates `DataSource`, `Function`, and `Decode` in addition to base shading pointers.

## Rendering Control Flow
- `gs_shading_fill_path` allocates a clipping path when the target device's `pattern_manage(..., pattern_manage__shading_area)` indicates clipping should be managed.
- It intersects the device clipping box, optional caller rectangle, shading BBox, and optional path.
- Axis-aligned BBoxes can be folded into the fixed clipping rectangle; otherwise a temporary path is built and intersected.
- If `Background` is set and requested, it remaps background color into a device color and fills the clip box before rendering the shading.
- It converts device fixed clip bounds back to user-space rectangle and calls `gs_shading_fill_rectangle(psh, ...)`, dispatching through the shading's procedure table.

## Dependencies
Uses color spaces, functions, data sources, device clipping, paths, pattern/shading helpers, and rendering callbacks from `gxshade*` modules. Type-specific fill implementations are external (`gxshade1.c`, `gxshade4.c`, `gxshade6.c`, etc.).

## Risks and Notes
- The background fill comment warns it is wrong for non-idempotent RasterOps.
- Actual shading algorithms are not in this file; this file only constructs objects and prepares clipping/background for dispatch.
- Domain-superset checking for functions is intentionally not enforced to match Adobe behavior.
