# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.c

## Purpose
Implements clipping path storage, sharing, assignment, rectangle-list representation, path synthesis, clipping intersection, scaling, enumeration, and debug printing. It deliberately excludes the lower-level actual clipping algorithms implemented in adjacent files.

## Public Surface
- Allocation/init/free: `gx_cpath_init_contained_shared`, `gx_cpath_alloc_shared`, `gx_cpath_init_local_shared`, `gx_cpath_free`.
- Sharing/assignment: `gx_cpath_unshare`, `gx_cpath_assign_preserve`, `gx_cpath_assign_free`.
- Accessors: `gx_cpath_to_path`, `gx_cpath_inner_box`, `gx_cpath_outer_box`, `gx_cpath_includes_rectangle`, `gx_cpath_set_outer_box`, `gx_cpath_list`.
- Setting/intersection/scaling: `gx_cpath_from_rectangle`, `gx_cpath_reset`, `cpath_is_rectangle`, `gx_cpath_clip`, `gx_cpath_intersect`, `gx_cpath_scale_exp2_shared`.
- Clip-list operations: `gx_clip_list_init`, `gx_clip_list_free`.
- Enumeration: `gx_cpath_enum_init`, `gx_cpath_enum_next`, `gx_cpath_enum_notes`.

## Implementation
- Represents clips either as a valid path or as a rectangle list with correct bounding boxes; paths are synthesized lazily from rectangle lists for `clippath`-style consumers.
- Uses reference-counted rectangle lists, path segment storage, and path-list nodes to share clip state across graphics states without unnecessary copying.
- Fast-paths rectangle clipping by intersecting boxes and preserving a valid path when the new clip is a rectangle and unchanged or simply represented.
- For nontrivial path intersections, flattens curves if needed, calls `gx_cpath_intersect_path_slow`, and stores original path history in a path-list when the rectangle list alone cannot preserve source path identity.
- Enumerates rectangle-list clipping paths by tracing rectangle edges and emitting path operations.
- Maintains `inner_box` for quick containment tests and `outer_box` expanded to pixel boundaries.

## Dependencies
Uses Ghostscript path, fixed-point, graphics state, imager state, clipping accumulator/list types, memory descriptors, and reference-count helpers.

## Risks and Notes
- `gx_cpath_unshare` has an explicit `NYI` comment where copying a shared rectangle list should occur.
- Several error returns in assignment helpers convert negative codes to `0`, matching old code style but obscuring failure propagation.
- Sharing local path segments is treated as fatal because stack-local segment storage cannot safely be reference-counted across clip paths.
- Rectangle-list enumeration can produce many small line segments for complex clips.

Filesystem relevance: none. This is graphics clipping-path infrastructure.
