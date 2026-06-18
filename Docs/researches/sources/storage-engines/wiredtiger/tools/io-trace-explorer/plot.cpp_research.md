# sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp

### Purpose
`plot.cpp` implements the interactive trace plot widgets and synchronized plot groups. It renders operation intervals into a pixbuf, draws axes and titles with Cairo, and supports inspect, move, zoom, undo, redo, reset, and synchronized X-axis navigation across plots.

### Important APIs, Types, and Functions
`plot_widget` construction registers draw and drag handlers, calculates top-level x/y ranges from operations, and initializes view state. Drag handlers clamp coordinates into the plot area, update move/zoom state, and draw inspect crosshairs or zoom rectangles. `set_view`, `view_sync`, `view_back`, `view_forward`, `view_reset`, `zoom_in`, and `zoom_out` manage view state and history. `render_worker` paints a subset of operations into the shared pixbuf. `on_draw` handles background, title, cached pixbuf rendering, threaded data drawing, overlays, and axes. `plot_group` owns plot registration and shared X-axis sync.

### Control Flow
Rendering starts in GTK's draw callback. If the pixbuf is absent, resized, or view-changed, `on_draw` allocates a new RGB pixbuf, binary-searches the timestamp-sorted operations for the visible window, splits work across one or eight threads, joins them, and then paints the pixbuf. User gestures call drag callbacks; move gestures set a shifted view in place, while zoom end converts selected viewport coordinates back to data coordinates and commits the view. Group-level navigation iterates plots and invokes individual history functions.

### State and Persistence
Each plot stores current/toplevel views, undo/redo stacks, drag coordinates and mode flags, cached pixbuf and view, margins, active tool, and a reference to immutable trace data. No state is persisted. Plot group stores a vector of plot pointers and the active plot pointer.

### Dependencies and Integration Points
The module depends on GTKmm, Cairo, Gdk Pixbuf, STL algorithms/threads, `io_trace_operation` ordering, and `current_time`. It is used by `main_window` and depends on `io_trace_collection` having already loaded sorted operations.

### Risks and Test Signals
The constructor indexes `ops[0]` and `ops[ops.size()-1]`, so empty traces are unsafe. `render_worker` has a likely bounds bug: it checks `y2 >= pixbuf_width` instead of `pixbuf_height`. Multiple worker threads write to the same pixbuf without synchronization, so overlapping operations can race; the visual result may be acceptable but is not data-race safe in C++. The pixbuf cache invalidation compares `_pixbuf->get_height()` to full widget `height` instead of `pixbuf_height`, causing extra rerenders. Division by zero can occur in move math if the drawable area is zero. Tests should cover coordinate transforms, view history, empty/single-operation traces, zoom/move gestures, rendering under ThreadSanitizer, and screenshot checks for axes/data after resizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/plot.cpp -->
