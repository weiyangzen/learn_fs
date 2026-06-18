# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.c

Common support routines shared by IJG command-line applications such as `cjpeg`, `djpeg`, and `jpegtran`.

Key behavior:
- Under `NEED_SIGNAL_CATCHER`, installs handlers for `SIGINT`/`SIGTERM`; the handler suppresses tracing, calls `jpeg_destroy`, and exits to clean memory/temp files.
- Under `PROGRESS_REPORT`, defines `progress_monitor`, `start_progress_monitor`, and `end_progress_monitor` for stderr percentage output across library and application extra passes.
- `keymatch` performs case-insensitive matching of possibly abbreviated command-line switches with a minimum abbreviation length.
- `read_stdin` and `write_stdout` put standard streams into binary mode using optional `setmode` or `fdopen` portability hooks.

Dependencies:
- Includes `cdjpeg.h`, ctype, and optional signal/fcntl/io headers.
- Calls IJG common APIs such as `jpeg_destroy`.
- Relies on compile-time feature macros from `jconfig.h`.

Research notes:
- Most code is conditional portability glue.
- The signal handler uses a single static `sig_cinfo`, so it is intended for one active JPEG object per process.
- Binary-mode handling is critical for non-Unix platforms but usually inert on Plan 9/Unix-like environments.
