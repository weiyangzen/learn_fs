# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msprn.c

Windows `%printer%` IODevice implementation.

Key behavior:
- Registers a FileSystem IODevice named `%printer%`.
- Validates the requested printer name with `OpenPrinter`.
- Creates a binary pipe and returns a `FILE *` for the write end.
- Starts a background thread that reads the printer name and print bytes from the pipe.
- The thread opens the printer, starts a RAW document, writes data with `WritePrinter`, and ends or aborts the job.
- Close waits up to 60 seconds for the print thread and closes its duplicated handle.

Notable dependencies:
- Windows spooler APIs and Microsoft runtime `_pipe`, `_beginthread`, and handle duplication.
- Ghostscript IODevice and product-name definitions.

Research notes:
- Win32s is rejected because it lacks required pipe and printer APIs.
- The printer name is sent through the pipe to avoid more complex thread synchronization.
