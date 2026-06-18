# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msprn.c

Read status: complete.

Purpose: `%printer%` IODevice for MS-Windows, allowing `-sOutputFile="%printer%Printer Name"`.

Main logic:
- Defines `gs_iodev_printer` with `%printer%` prefix.
- Allocates per-device state containing a duplicated thread handle.
- `mswin_printer_fopen` validates the printer with `OpenPrinter`, creates a binary pipe, exposes the pipe write end as `FILE *`, starts a thread for the pipe read end, duplicates the thread handle, and writes the printer name into the pipe.
- `mswin_printer_thread` reads the printer name, lazily opens the Windows printer, starts a RAW print job, copies pipe data through `WritePrinter`, and ends or aborts the job.
- `mswin_printer_fclose` closes the pipe stream, waits up to 60 seconds for the print thread, closes the handle, and clears state.

Filesystem/storage relevance:
- Implements printer output as a Ghostscript file device over Windows spooler APIs.
- Uses pipes to bridge C `FILE *` output to printer APIs.

Notable behavior:
- Explicitly rejects Win32s because pipes and Win32 printers are unsupported there.
- Uses `gp_file_name_sizeof` bytes at the start of the pipe as an ad hoc printer-name message.
