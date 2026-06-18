# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dvx.c

Read status: complete.

Purpose: DesqView/X-specific Ghostscript platform routines.

Main logic:
- Provides no-op `gp_init` and `gp_exit`, and `gp_do_exit` wrapping `exit`.
- `gp_strerror` delegates to C `strerror`.
- `gp_get_realtime` uses `gettimeofday` and returns seconds plus nanoseconds.
- `gp_get_usertime` approximates user time with real time.
- Persistent cache functions are stubs: insert returns `0`, query returns `-1`.
- `gp_open_printer` maps empty name or `PRN` to `stdprn`, optionally binary, otherwise opens a named file.
- `gp_close_printer` flushes `stdprn` or closes file.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides printer/file opening behavior and cache stubs for a DOS-like platform.
