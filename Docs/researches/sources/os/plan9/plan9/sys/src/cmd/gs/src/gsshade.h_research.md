# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.h

## Purpose
Defines the public shading parameter structures, generic shading type/procedure model, per-shading constructors, and the single public path-fill rendering entry point.

## Public Surface
- `gs_shading_type_t`: shading types 1 through 7: function-based, axial, radial, free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, tensor-product patch.
- `gs_shading_params_t`: common `ColorSpace`, optional `Background`, optional `BBox`, and `AntiAlias`.
- `gs_shading_procs_t` and `SHADING_FILL_RECTANGLE_PROC`: per-type rectangle rendering callback contract.
- Concrete parameter structs for each shading type.
- Parameter initialization and constructor prototypes for all seven types.
- `gs_shading_fill_path_adjusted(...)`: fill path/rectangle with a shading.

## Data Model
- `gs_shading_t` is a generic header plus common params; concrete public structs are represented by type-specific parameter structs and private implementation structs declared in internal headers.
- Mesh shadings share `gs_shading_mesh_params_common`: `DataSource`, coordinate/component bit depths, `Decode`, and optional `Function`.
- GC descriptor macros are provided for generic, function, axial/radial, mesh, and concrete mesh shading structs.

## Dependencies
Includes client color, color space, data source, function, matrix, and fixed-point headers. It forward-declares `gx_device`, `gx_path`, `gs_imager_state`, and `gs_shading_t` as needed.

## Risks and Notes
- Clients are responsible for setting required fields marked by comments before calling constructors.
- `gs_shading_fill_rectangle` may paint outside the requested user-space rectangle unless the caller has prepared clipping; the public path-fill routine handles this for external callers.
