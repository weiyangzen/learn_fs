# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.c

Core Ghostscript fixed-point path construction and memory-management implementation. It owns path allocation modes, shared segment reference-counting, subpath/segment creation, incremental path mutation, charpath transfer behavior, closepath handling, and debug printing.

Key behavior:
- Defines structure descriptors for path objects and segment types, plus default path procedure tables and a bbox-accumulator procedure table.
- Supports heap-allocated, contained, and stack/local paths, with separate reference-counted segment storage.
- Prevents sharing of local segment storage; attempts to share local segments are treated as fatal.
- `gx_path_unshare` and `path_alloc_copy` implement copy-on-write before mutation.
- Constructors add moveto, rmoveto, lines, multiple lines, rectangles, curves, partial arcs, whole paths, and charpath-specific variants.
- `gx_path_add_path` physically splices subpath segment chains from one path into another, then resets the source path.
- Closepath allocates `line_close_segment`, links it to the current subpath, and records the source subpath.
- `gx_path_pop_close_notes` removes the final line and replaces it with closepath for Type 1 font hinting workflows.
- Debug builds can dump complete segment chains with coordinates and notes.

Notable dependencies:
- `gzpath.h` for concrete path/segment internals.
- `gsstruct.h` for GC descriptors and reference-counting macros.
- `gxfixed.h` for fixed-point coordinates.
- `vdtrace.h` for optional visual tracing.

Research notes:
- Memory ownership is subtle: path objects and segment containers have separate allocation modes and lifetimes.
- `gx_path_add_lines_notes` intentionally does not roll back partial additions on allocation/range failure, matching repeated single-line calls.
- Bounding-box enforcement via `bbox_set` rejects points outside a preset bbox during construction.
