# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs16spl.c

Purpose: Win32s/Win16 helper application that sends Ghostscript printer output files to the 16-bit Windows spooler.

Key interfaces: `spoolfile`, `SpoolDlgProc`, `init_window`, and `WinMain`.

Control flow: parses command-line `port filename`, creates a modeless dialog, opens the file, opens a spool job, starts a spool page, streams the file in 16 KiB chunks with progress UI updates, pumps window messages, and either closes or deletes the spool job depending on errors/cancel.

Dependencies: Uses Win16 spooler APIs (`OpenJob`, `WriteSpool`, etc.), Windows dialog/message APIs, and C stdio.

Risks and notes: Command-line parsing is space-delimited and does not support quoted filenames. Global state (`error`, `hJob`, buffers, window handle) is used throughout. Error handling reports only coarse messages.
