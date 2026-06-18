<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py -->
# sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py

Purpose: finds core dumps and prints/saves debugger stack traces for Evergreen diagnostics.

Important APIs: `border_msg()` formats section headers. `LLDBDumper` and `GDBDumper` locate debuggers and run batch commands. GDB supports optional shared-library search path and writes all-thread backtraces to `<core-base>.stacktrace.txt` after printing a shorter trace to stdout.

Control flow: `main()` parses core and library paths, ensures `~/.gdbinit` contains `/data/mci` auto-load safe path, recursively finds files matching `dump.*core`, uses `file` output to extract `execfn`, adjusts executable path for non-Python cores when needed, then dispatches to GDB on Linux. macOS/Windows branches are placeholders.

State and persistence: mutates `~/.gdbinit` and writes stacktrace text files in the current directory. Reads core files only.

Dependencies and integration: Evergreen post task `dump stacktraces`. Depends on `file`, `gdb` or `lldb`, core files preserving `execfn`, and debug symbols/library paths.

Risks and test signals: `file` output parsing is regex/string based. If `execfn` is missing, the core is skipped. GDB absence exits the script. Output file handles are opened without explicit close but process exit closes them.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py -->
