# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix.c

Purpose: Provides Unix-specific Ghostscript platform hooks for initialization, exit, clocks, display environment, printer files, and placeholder font enumeration.

Key interfaces: `gp_init`, `gp_exit`, `gp_do_exit`, `gp_strerror`, `gp_read_macresource`, `gp_get_realtime`, `gp_get_usertime`, `gp_getenv_display`, `gp_open_printer`, `gp_close_printer`, and `gp_enumerate_fonts_*`.

Control flow: initialization and cleanup are no-ops; program termination delegates to `exit`. Real time uses `gettimeofday`, with a compatibility branch for old SVR4 signatures and validation of `tv_usec`. User time either sums `times()` counters when configured or falls back to real time. Printer open simply opens a named file in text or binary write mode, while close conditionally uses `pclose` for pipe-style names.

Dependencies: Uses Unix headers via Ghostscript wrappers, `gsexit.h`, `gp.h`, `getenv`, `fopen`, `pclose`, `times`, and `gettimeofday`.

Risks and notes: `gp_open_printer` does not actually open pipe commands even though `gp_close_printer` checks `fname[0] == '|'`; pipe opening likely belongs to another platform variant or is incomplete here. `gp_strerror` returns `NULL`, so callers must tolerate missing OS error text.
