# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath2.c

`gxpath2.c` implements path access, bbox maintenance, rectangle recognition, transforms, reversal, and enumeration.

`gx_path_current_point` and `gx_path_subpath_start_point` return fixed-point positions or `nocurrentpoint`. `gx_path_bbox` lazily updates the stored bbox by scanning segments after `box_last`; curve control points are included. If the path has only a current point, that point is used. `gx_path_bbox_set` honors explicit `setbbox`.

Rectangle detection is handled by `gx_subpath_is_rectangular`, recognizing open rectangles, closepath rectangles, lineto-closed rectangles, and paths containing both lineto-to-start and closepath. `gx_path_is_rectangular` only succeeds for single-subpath paths.

`gx_path_translate` mutates bbox, current point, segment endpoints, and curve controls. `gx_point_scale_exp2`, `gx_rect_scale_exp2`, and `gx_path_scale_exp2_shared` scale points/paths by powers of two, optionally skipping shared segment mutation.

`gx_path_copy_reversed` emits reversed subpaths with Adobe-compatible closepath behavior. It preserves segment notes and handles trailing moveto semantics.

The enumerator functions initialize direct path iteration, return moveto/lineto/curveto/closepath events, expose last segment notes, and support one-or-more-element backup. Invalid segment types are treated as fatal.
