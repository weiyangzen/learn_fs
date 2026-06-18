# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.c

Read status: complete.

Purpose: Classic Mac OS / Carbon platform support routines excluding the larger file-I/O implementation in `gp_macio.c`.

Main logic:
- Includes Classic Mac toolbox headers or Carbon.
- Defines global `HWND hwndtext` used as a DLL-instance-style identifier.
- `mygetenv` returns `NULL`.
- `gp_init`, `gp_exit`, and `gp_do_exit` provide minimal lifecycle behavior.
- Implements a `gettimeofday` shim and Ghostscript real/user time functions.
- `gp_get_usertime` approximates user time from real time and subtracts a random byte, apparently for seed variation on fast systems.
- `gp_strerror` returns `NULL`.
- Provides alternate clock helpers `gp_get_clock`, `gpp_get_clock`, `gpp_get_realtime`, and `gpp_get_usertime`.
- Persistent cache functions are stubs.
- Console/display helpers are no-ops or return `NULL`.

Filesystem/storage relevance:
- Minimal. Mac filesystem/resource work is in `gp_macio.c`.
- Cache stubs mean no persistent storage backing here.

Notable behavior:
- Contains legacy/commented code and old Mac date conversion logic.
- Error-string support is unimplemented.
