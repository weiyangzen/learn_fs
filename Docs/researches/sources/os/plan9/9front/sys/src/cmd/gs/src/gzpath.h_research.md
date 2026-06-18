# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzpath.h

Defines Ghostscript’s internal path representation and path helper APIs.

Key points:
- Paths are linked lists of `segment` objects: start, line, close-line, and Bezier curve.
- `segment_common` stores previous/next links, type, notes, and endpoint.
- `subpath` is a start segment that owns the current subpath’s last segment, curve count, temporary closer, and closed flag.
- Curve helpers convert between control points and cubic coefficients and support flattening, monotonic splitting, and subdivision.
- Path state flags track current point validity, open subpath state, drawing state, and out-of-range coordinates.
- `gx_path_segments` carries reference-counted shared segment ownership.
- `gx_path_s` stores allocator, allocation mode, segment ownership, bbox, current position, counts, state flags, and virtual path procedure table.
- Declares GC descriptors for path segments, paths, and path enumerators.
- Defines inline helpers for shared/void/curve checks and current-point retrieval.
- Defines `gx_flattened_iterator_s` and functions for forward/backward iteration over flattened curves or lines.

Research notes:
- This is one of the core geometry data structures in the graphics library.
- Segment sharing and stack-contained temporary paths are explicit design concerns.
