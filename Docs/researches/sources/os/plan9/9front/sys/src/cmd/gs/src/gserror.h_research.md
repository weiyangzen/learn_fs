# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserror.h

This header defines Ghostscript error-return helper macros.

API:
- `gs_log_error(int, const char *, int)` logs an error code with file and line in debug builds.
- In non-debug builds, `gs_log_error` is macro-redefined to return the error unchanged.
- `gs_note_error(err)` records the current source file and line.
- `return_error(err)` returns `gs_note_error(err)`.

This is used throughout the batch to preserve source-location diagnostics in debug builds while keeping release builds cheap.
