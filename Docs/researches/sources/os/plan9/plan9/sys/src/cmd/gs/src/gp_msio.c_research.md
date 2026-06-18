# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msio.c

Read status: complete.

Purpose: Microsoft Windows text-window stdio integration for Ghostscript DLL-style use.

Main logic:
- Defines a pseudo IODevice `gs_iodev_wstdio` whose init patches `%stdin`, `%stdout`, and `%stderr` if the underlying file is a console.
- Replacement stream open procedures attach custom process/available callbacks and detach from ordinary `FILE *`.
- `win_std_read_process` requests input through `pgsdll_callback(GSDLL_STDIN, ...)`.
- `win_std_write_process` sends output through `pgsdll_callback(GSDLL_STDOUT, ...)`.
- `win_std_available` reports EOF/unknown availability.
- Overrides `fprintf` on Windows compiler configurations: console output is formatted into a local buffer and sent to the DLL callback; non-console files use `vfprintf`.

Filesystem/storage relevance:
- Affects standard streams and console-backed file devices.
- No filesystem enumeration or path handling.

Notable behavior:
- Uses a 1024-byte local buffer with `vsprintf` in `fprintf`, so long formatted messages can overflow in historical builds.
- The pseudo-IODevice init is described in comments as poor architecture.
