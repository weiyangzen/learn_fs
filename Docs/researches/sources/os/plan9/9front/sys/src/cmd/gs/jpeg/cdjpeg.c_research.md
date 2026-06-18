# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.c

Common runtime support routines for IJG command-line applications.

Key points:
- Optionally installs signal handlers (`enable_signal_catcher`) for `SIGINT` and `SIGTERM` when `NEED_SIGNAL_CATCHER` is enabled, calling `jpeg_destroy` before process exit so temporary files and JPEG memory are cleaned up.
- Optional progress-monitor support (`PROGRESS_REPORT`) prints percent completion to stderr, including extra application-level passes not known to the JPEG library.
- `keymatch` performs case-insensitive, minimum-length abbreviation matching for command-line switches.
- `read_stdin` and `write_stdout` put standard streams into binary mode where required, using `setmode` or `fdopen` depending on configured macros.

Dependencies and interactions:
- Includes `cdjpeg.h`, ctype, and optionally signal/fcntl/io headers.
- Called by `cjpeg.c` and `djpeg.c` for option parsing, binary stdio setup, progress display, and temporary-file cleanup.
- The signal catcher stores one global `j_common_ptr`, so it is aimed at single active JPEG command-line processes.

Risk notes:
- Signal cleanup depends on a global pointer and calls nontrivial cleanup from a signal handler; this reflects historical portability goals rather than modern async-signal-safety practice.
- Progress percentage divides by `pass_limit`; callers rely on IJG progress manager invariants to avoid invalid limits.
- Binary stdio reopening is highly platform-dependent and controlled by `jconfig.h`.
