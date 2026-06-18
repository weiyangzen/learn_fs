# sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp -->
## sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp

### Purpose
`main.cpp` defines the GTK application class and command-line entry point for `IOTraceExplorer`.

### Important APIs, Types, and Functions
`io_trace_explorer` subclasses `Gtk::Application` with `Gio::Application::Flags::HANDLES_COMMAND_LINE`. `on_command_line` registers `--quiet`, parses input filenames, loads each into `_traces`, logs timing through GLib messages, and activates the UI. `on_activate` creates a `main_window`, adds it to the application, shows it, and focuses it. `main` simply runs an instance.

### Control Flow
GTK invokes `on_command_line`; the code parses arguments from `Gio::ApplicationCommandLine`, rejects missing inputs, loads all trace files synchronously on the command-line path, then calls `activate()`. Exceptions are caught and reported through `g_error`, returning failure.

### State and Persistence
The application owns one `io_trace_collection` for the process lifetime and a raw `_main` window pointer. It does not persist state or remember open files.

### Dependencies and Integration Points
It depends on GTKmm/Glibmm, `io_trace_collection`, `main_window`, plotting declarations, and `current_time`. It bridges trace loading and display construction.

### Risks and Test Signals
`optind` is used after Glib option parsing; this assumes global getopt state lines up with GTK parsing. Loading is synchronous before the window appears, so large traces can delay startup. `_main` is raw and never deleted explicitly. Tests should cover argument parsing, no-input failure, multi-file loading, `--quiet`, and startup with malformed files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/io-trace-explorer/main.cpp -->
