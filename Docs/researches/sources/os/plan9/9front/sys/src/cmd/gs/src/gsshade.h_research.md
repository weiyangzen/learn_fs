# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.h

Defines public shading parameter structures, type tags, GC descriptor macros, constructors, and the rendering entry point.

Key definitions:
- `gs_shading_type_t` enumerates shading types 1 through 7.
- `gs_shading_params_common` contains color space, optional background, optional BBox, and AntiAlias.
- `gs_shading_procs_t` currently contains the type-specific `fill_rectangle` procedure.
- Type-specific parameter structs cover Function-based, Axial, Radial, and four mesh shading families.
- Mesh common parameters include data source, coordinate/component bit depths, Decode, and optional Function.
- Descriptor macros define how each shading type participates in Ghostscript GC traversal.

Public API:
- Parameter initializers for each shading type.
- `gs_shading_*_init` constructors.
- `gs_shading_fill_path_adjusted`, the external path/rectangle shading renderer.

Research notes:
- The header keeps implementation layout partially visible because GC descriptors and clients need concrete parameter structures.
