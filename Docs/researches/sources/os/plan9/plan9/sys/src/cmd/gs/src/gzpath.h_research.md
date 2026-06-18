# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzpath.h

Defines Ghostscript’s internal path representation. Paths are linked lists of start, line, close-line, and Bezier curve segments, with subpaths holding closure state and curve counts.

Key structures and mechanics:
- `segment`, `line_segment`, `line_close_segment`, `curve_segment`, `subpath`.
- Curve point/coefficient conversion macros and monotonic/flattening procedure declarations.
- `gx_path_state_flags`: tracks current point validity, open subpath, drawing state, and out-of-range coordinates.
- `gx_path_segments`: ref-counted shared segment ownership.
- `gx_path_s`: full path object with allocator, bounding box, segment ownership, state flags, counts, current position, and virtual path procs.
- `gs_path_enum_s` and `gx_flattened_iterator_s`: enumeration/flattening state.

This is a core geometry header. The main invariants are path state flags, segment reference ownership, and GC descriptors for shared path structures.
