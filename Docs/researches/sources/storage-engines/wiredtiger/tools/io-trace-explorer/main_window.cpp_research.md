# sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp

### Purpose
`main_window.cpp` builds the GTK application window: toolbar controls, vertically split plot widgets, status bar, keyboard shortcuts, and plot-tool coordination.

### Important APIs, Types, and Functions
The constructor creates one `plot_widget` per trace, resets shared X extents, wires toolbar buttons/toggles, nests plots in vertical `Gtk::Paned` containers, installs an `EventControllerKey`, and sets window defaults. `set_plot_tool` updates every plot and blocks toggle signal recursion while syncing button states. Event handlers route back/forward/reset and zoom to `plot_group` or the active plot.

### Control Flow
Construction iterates the trace map to create plots, then uses `last_plot`/`last_paned` state to assemble either a single plot or a chain of split panes. Toolbar and key events later call handlers that update plot state and queue redraws through the plot layer.

### State and Persistence
The window stores raw pointers to heap-allocated `plot_widget` and `Gtk::Paned` instances in vectors. The destructor contains a TODO and does not delete them, relying on GTK object ownership or process teardown. View history lives inside each plot and the group.

### Dependencies and Integration Points
It depends on GTKmm widgets/signals, `io_trace_collection`, `plot_group`, and `plot_widget`. It is constructed by `main.cpp` after trace parsing and owns the visible user interaction surface.

### Risks and Test Signals
If there are zero traces, the window will show only toolbar/status with no plot; if a trace has zero operations, `plot_widget` construction can fail. Raw allocation and uncertain GTK ownership are memory-risk areas. Shortcut tests should verify undo/redo, zoom in/out, tool selection, and reset. UI tests should verify one trace, multiple traces, and no trace layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.cpp -->
