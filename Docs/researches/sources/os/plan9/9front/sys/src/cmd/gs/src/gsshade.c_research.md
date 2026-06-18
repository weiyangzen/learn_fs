# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.c

Implements constructors, validation, GC descriptors, and common rendering setup for PDF/PostScript shading objects.

Key behavior:
- Defines GC descriptors for generic shadings and mesh shadings, including data sources, functions, and decode arrays.
- Initializes common shading parameters and mesh-specific defaults.
- Validates color spaces, BBoxes, function input/output arity, mesh bit depths, and BitsPerFlag values.
- Provides parameter init and object allocation for Function-based, Axial, Radial, Free-form Gouraud triangle, Lattice Gouraud triangle, Coons patch, and Tensor product patch shadings.
- Rendering entry `gs_shading_fill_path_adjusted` delegates to `gs_shading_fill_path`, which builds clipping from the current device box, optional rectangle, optional shading BBox, and optional input path.
- Uses a temporary clip device when the target device requests shading-area clipping through `pattern_manage`.
- Fills the shading background when requested, remapping the background color through the shading color space.
- Calls the shading-type `fill_rectangle` procedure after converting the clipped device box back to user-space bounds.

Dependencies:
- Uses color spaces, functions, data sources, clip paths, path construction, device color remapping, and shading renderers from `gxshade*`.

Research notes:
- Function domain superset checking is intentionally not enforced to match Adobe behavior.
- Background fill has an in-source warning that it is wrong for non-idempotent RasterOps.
