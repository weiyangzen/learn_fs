# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath1.c

Additional path operators: arcs, arct/arcto, clipping/path conversion, flattening, reverse, stroke-to-path, dashpath, path bounding boxes, and `pathforall`.

`common_arc` parses five numeric operands and dispatches to `gs_arc` or `gs_arcn`. `common_arct` supports both `arct` and `arcto`, returning tangent points for `arcto`. Other single-step operators call `gs_clippath`, `gs_dashpath`, `gs_flattenpath`, `gs_reversepath`, `gs_strokepath`, or `gs_pathbbox`.

`pathforall` uses a graphics-library path enumerator and execution-stack continuation. It stores four procedure operands, enumerates path segments, pushes segment coordinates, and invokes the matching procedure for moveto/lineto/curveto/closepath. `path_cleanup` releases the enumerator if execution aborts. The pathforall implementation is a controlled callback loop into PostScript code.
