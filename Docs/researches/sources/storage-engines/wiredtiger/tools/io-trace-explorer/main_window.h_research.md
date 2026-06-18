# sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h

### Purpose
`main_window.h` declares the `main_window` GTK application window class and its UI state.

### Important APIs, Types, and Functions
The class extends `Gtk::ApplicationWindow` and exposes a constructor taking `io_trace_collection&`. Protected members include toolbar buttons/toggles, signal connections, plot group, vectors of plots/panes, status bar, `set_plot_tool`, and handlers for toggles, navigation, zoom, reset, and key presses.

### Control Flow
The header defines callback boundaries used by GTK signals. The implementation dispatches all user events through these handlers to plot state.

### State and Persistence
State is transient UI state: active tool toggles, plot/pane object pointers, and shared plot group. Nothing is saved to disk.

### Dependencies and Integration Points
It depends on `gtkmm.h`, `io_trace.h`, and `plot.h`; `main.cpp` includes it to create the top-level window.

### Risks and Test Signals
The header exposes raw pointer vectors without ownership semantics. Any future refactor should clarify whether GTK owns these children or whether `main_window` must delete them. Compile tests and static analysis around object lifetime are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main_window.h -->
