# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mshdl.c

Windows `%handle%` IODevice implementation.

Key behavior:
- Registers `gs_iodev_handle` as a FileSystem IODevice named `%handle%`.
- Parses a hexadecimal OS handle from the filename suffix.
- Converts the OS handle to a C file descriptor with `_open_osfhandle`.
- Wraps the descriptor in a `FILE *` using `fdopen`.
- Closes the stream on IODevice close.

Notable dependencies:
- Windows/MS C runtime `<io.h>` handle functions.
- Ghostscript IODevice interfaces from `gxiodev.h`.

Research notes:
- Comments note the handle-size assumptions are correct for Win32 and maybe wrong for Win64.
- Intended for callers that pass pipe or file handles to Ghostscript output.
