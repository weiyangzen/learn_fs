# sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h

### Purpose
`plot.h` declares plotting primitives for the I/O Trace Explorer: coordinate transforms, interaction modes, individual plot widgets, and synchronized plot groups.

### Important APIs, Types, and Functions
`plot_view` stores data extents and provides `data_to_view_x`, `data_to_view_y`, `view_to_data_x`, `view_to_data_y`, equality, and inequality. `plot_tool` enumerates `NONE`, `INSPECT`, `MOVE`, and `ZOOM`. `plot_widget` extends `Gtk::DrawingArea` with public navigation/zoom methods and active-tool accessors, protected draw/drag/view methods, and render internals. `plot_group` exposes group-level back/forward/reset/reset-X/sync and active-plot lookup.

### Control Flow
The header defines the methods implemented in `plot.cpp`. Coordinate conversions are inline and called during rendering and gestures.

### State and Persistence
The declared state is transient UI state: current/toplevel/cached views, history stacks, drag flags, margins, pixbuf, and references to trace/group. There is no disk persistence.

### Dependencies and Integration Points
It depends on GTKmm, Glibmm, and `io_trace.h`. `main_window` uses the public API to switch tools and navigate. `plot.cpp` relies on the inline conversion semantics for all drawing.

### Risks and Test Signals
`plot_view` equality compares doubles exactly, acceptable for cached view assignment but risky if future code performs incremental floating-point operations. `plot_widget` stores references, so the trace collection and group must outlive widgets. Tests should exercise transform round-trips and group sync invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.h -->
