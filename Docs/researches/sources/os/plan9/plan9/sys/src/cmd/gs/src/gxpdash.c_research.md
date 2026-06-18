# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpdash.c

`gxpdash.c` expands dashed paths into explicit path segments. It assumes the input path has no curves.

`gx_path_add_dash_expansion` reads current dash parameters from the imager state's line params. If no dash pattern is active, it copies the path unchanged. Otherwise it walks each subpath and calls `subpath_expand_dashes`.

`subpath_expand_dashes` starts with a moveto, then walks line and close segments while consuming dash pattern elements. It transforms device-space segment deltas back through `gs_imager_idtransform` to compute user-space dash lengths. When dash adaptation is enabled, it rescales the pattern to fit an integral number of repetitions along the segment.

Ink-on sections emit lines; ink-off sections emit movetos. Closed subpaths with initial ink-on dashes use a two-pass wraparound scheme so the initial skipped section can be emitted at the end. Degenerate segments are skipped unless round caps are active. Near-zero trailing off elements may be stretched to produce a dot.

The function preserves segment notes where possible and propagates path-construction errors.
