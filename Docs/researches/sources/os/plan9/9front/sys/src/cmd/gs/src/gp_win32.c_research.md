# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_win32.c

Purpose: Common Win32 platform routines.

Key behavior: `gp_strerror` delegates to ANSI `strerror`. `gp_get_realtime` uses `GetSystemTime` and computes seconds/nanoseconds since January 1, 1980 in UTC. `gp_get_usertime` aliases realtime.

Console and naming: `gp_file_is_console` treats stdin/stdout/stderr file descriptors as console, with DLL-specific handling for null `FILE *`. `gp_getenv_display` returns `NULL`. It defines Windows scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Dependencies and notes: Includes Ghostscript memory/error headers and `windows_.h`. This file supplies only shared Win32 basics; file enumeration, printing, and environment details live elsewhere.
