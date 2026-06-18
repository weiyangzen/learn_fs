# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix.c

Purpose: Unix-specific non-filesystem platform routines for Ghostscript.

Key behavior: `gp_init` and `gp_exit` are no-ops; `gp_do_exit` delegates to C `exit`. `gp_strerror` returns `NULL`, so callers cannot rely on platform error text here. `gp_read_macresource` is stubbed out and returns zero.

Time, display, printer: `gp_get_realtime` uses `gettimeofday`, adapting to old SVR4 signatures and converting microseconds to nanoseconds. `gp_get_usertime` either uses `times` when configured or aliases realtime. `gp_getenv_display` reads `DISPLAY`. `gp_open_printer` opens a named file with text/binary write mode and returns null for an empty name; `gp_close_printer` uses `pclose` for pipe-like names and `fclose` otherwise.

Font enumeration: `gp_enumerate_fonts_init/next/free` are stubs, returning no native font list.
