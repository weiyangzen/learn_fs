# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdos.c

Read status: complete.

Purpose: common MS-DOS platform routines.

Main logic:
- `gp_strerror` delegates to C `strerror`.
- `gp_get_realtime` uses DOS interrupt calls to read date and time, converts to seconds since January 1, 1980, and returns hundredths as nanoseconds.
- `gp_get_usertime` approximates user time with real time.
- `gp_file_is_console` uses DOS ioctl device info to detect console/device handles, with DLL-specific handling for `NULL`.
- `gp_getenv_display` returns `NULL`.
- Defines DOS scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Filesystem/storage relevance:
- Provides console detection, null device naming, scratch prefix, and time support for DOS file/printer abstractions.

Notable behavior:
- Date conversion uses hand-coded leap-year arithmetic.
- Epoch differs from Unix; comments state January 1, 1980.
