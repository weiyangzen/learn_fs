# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2pr.c

Read status: complete.

Purpose: `%printer%` IODevice implementation for OS/2.

Main logic:
- Defines `gs_iodev_printer` with `%printer%` prefix.
- Device state stores selected queue name and temporary filename.
- `os2_printer_init` allocates and zeroes device state.
- `os2_printer_fopen` validates the queue through `pm_find_queue`, reports valid queue names on failure, creates a scratch file with `gp_open_scratch_file`, and returns it as the output stream.
- `os2_printer_fclose` closes the scratch stream, spools it with `pm_spool`, and unlinks it.

Filesystem/storage relevance:
- Implements OS/2 printer output as a Ghostscript file device staged through a temporary file.

Notable behavior:
- Comments mention a pipe/thread approach was preferable but did not work reliably in Ghostscript’s second thread on OS/2.
