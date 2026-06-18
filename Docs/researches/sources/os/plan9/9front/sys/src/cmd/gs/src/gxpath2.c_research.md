# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath2.c

Read-side and transformation support for Ghostscript fixed-point paths. It implements current-point queries, bbox maintenance, rectangular path recognition, translation/scaling, path reversal, and path enumeration.

Key behavior:
- `gx_path_current_point` and `gx_path_subpath_start_point` return current/start points or `nocurrentpoint`.
- `gx_path_bbox` lazily updates the cached bbox by scanning only segments after `box_last`; empty paths fall back to current point if present.
- `gx_path_bbox_set` honors explicit bboxes used by `patbbox`.
- `gx_subpath_is_rectangular` recognizes open, closed, fake-closed, and redundantly closed rectangles.
- `gx_path_translate` updates cached bbox, current point, segment endpoints, and curve controls.
- `gx_path_scale_exp2_shared` scales path metadata and, when segments are not shared, segment coordinates by powers of two.
- `gx_path_copy_reversed` reproduces Adobe reversepath behavior, including treatment of closepath and trailing moveto.
- Path enumeration returns moveto/lineto/curveto/closepath records, supports notes, and can back up one or more elements.

Notable dependencies:
- `gspath.h` for enumerator allocation prototype.
- `gxarith.h` and `gxfixed.h` for fixed-point arithmetic.
- `gzpath.h` for concrete segment traversal.

Research notes:
- Rectangle detection is intentionally tolerant of common bad PostScript that closes with both lineto and closepath.
- `gx_path_scale_exp2_shared` always scales bbox/current position but skips segment mutation when segments are shared; callers must pass the sharing flag correctly.
