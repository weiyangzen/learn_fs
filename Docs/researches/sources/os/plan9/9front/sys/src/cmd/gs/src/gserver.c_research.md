# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gserver.c

This file provides a simple procedural server front end to the Ghostscript interpreter, replacing the normal `gs.c` style entry point for embedding.

Public routines:
- `gs_server_initialize` wraps file descriptors with C `FILE *`, initializes Ghostscript in phases, sets `/QUIET true` and `/NOPAUSE true`, and optionally runs an initialization string.
- `gs_server_run_string` executes PostScript code and optionally reports the error object as text.
- `gs_server_run_files` executes a NULL-terminated list of files, either permanently modifying baseline state or within a temporary job save/restore.
- `gs_server_terminate` finalizes Ghostscript.

Job isolation:
- `job_begin` erases the page and saves interpreter state with `zsave`.
- `job_end` resets interpreter state and restores the saved object with `zrestore`.

Error reporting:
- `errstr_report` converts the PostScript error object with `obj_cvs`; if conversion fails, it emits `[unprintable]`.

This is an embedding convenience layer with rudimentary job-state management.
