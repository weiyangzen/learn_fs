# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_win32.c

Purpose: Supplies common Win32 platform helpers for Ghostscript: OS error strings, time, console detection, display environment, and standard filename constants.

Key interfaces: `gp_strerror`, `gp_get_realtime`, `gp_get_usertime`, `gp_file_is_console`, `gp_getenv_display`, `gp_scratch_file_name_prefix`, `gp_null_file_name`, and `gp_current_directory_name`.

Control flow: time uses UTC `GetSystemTime` and computes seconds since 1-Jan-1980 plus millisecond nanoseconds. User time is approximated by real time. Console detection treats `NULL` differently for DLL vs non-DLL builds and otherwise considers descriptors `<=2` console streams.

Dependencies: Uses Windows API wrappers, `strerror`, `fileno`, Ghostscript types/errors, and `gp.h`.

Risks and notes: Timezone is intentionally ignored. `gp_getenv_display` returns `NULL`, so display discovery is not supported here. Console detection is descriptor-based and may not cover redirected handles perfectly.
