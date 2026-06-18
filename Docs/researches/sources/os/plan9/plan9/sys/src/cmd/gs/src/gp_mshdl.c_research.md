# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mshdl.c

Read status: complete.

Purpose: `%handle%` IODevice for MS-Windows, allowing callers to pass an existing OS file handle to Ghostscript.

Main logic:
- Defines `gs_iodev_handle` with `%handle%` prefix.
- `get_os_handle` validates that the filename suffix is all hex digits and parses it as an unsigned long.
- `mswin_handle_fopen` converts the OS handle to a C file descriptor with `_open_osfhandle`, wraps it with `fdopen`, and returns the resulting `FILE *`.
- `mswin_handle_fclose` closes the stream.

Filesystem/storage relevance:
- Bridges Ghostscript file output to externally-created Windows handles, commonly pipes created by a parent process.

Notable behavior:
- Comments note the handle-width assumption is correct for Win32 and may be wrong for Win64.
- Invalid handles map through `gs_fopen_errno_to_code(EBADF)`.
