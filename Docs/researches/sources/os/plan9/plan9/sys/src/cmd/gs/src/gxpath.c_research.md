# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.c

`gxpath.c` implements mutable fixed-point path construction and path memory ownership. It uses Ghostscript's GC descriptors, fixed-point arithmetic, and internal `gzpath.h` segment definitions.

Paths own or share a reference-counted `gx_path_segments` object. Allocation supports heap paths, contained heap paths, stack-local paths, and a special bbox-accumulator pseudo-path. `gx_path_unshare` performs copy-on-write through `path_alloc_copy`. `gx_path_assign_preserve` and `gx_path_assign_free` carefully transfer segment ownership while preserving destination allocation class.

The incremental builder uses virtual `gx_path_procs`. Normal paths allocate concrete segments; bbox accumulator paths only update bbox/current-point state. Constructors include moveto, rmoveto, lineto, multi-line append, rectangle, curveto, partial arc approximation, path append, charpath append, closepath, and pop-closepath.

Segment allocation macros enforce unsharing, open subpaths when necessary, link new segments, and update state flags. `gx_path_add_partial_arc_notes` converts a small arc into one cubic Bezier using caller-supplied tangent fraction. `gx_path_add_char_path` implements charpath modes by appending actual outlines, bbox rectangles, bbox diagonals, or current points.

Debug-only routines dump path state and segment chains. Key risks are manual segment ownership, reliance on state flags, and partial additions in `gx_path_add_lines_notes` not being rolled back on mid-loop allocation failure.
