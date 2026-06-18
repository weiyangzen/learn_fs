# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs16spl.c

Purpose: Win32s/Win16 helper program that sends a Ghostscript output file to the 16-bit Windows spooler.

Flow: `WinMain` parses command line into `port` and `filename`, creates a modeless dialog, then calls `spoolfile`. `spoolfile` opens the file, starts a 16-bit spool job with `OpenJob`/`StartSpoolPage`, streams data in 16 KiB chunks via `WriteSpool`, updates dialog progress, pumps messages, and closes or deletes the job depending on error state.

UI behavior: `SpoolDlgProc` sets the dialog title and treats cancel as an error, destroying the dialog and posting quit. On failure, the window displays an error message and waits for user dismissal.

Dependencies and notes: Uses legacy Win16 spooler APIs declared manually from print headers. It exists because Win32s lacked both direct 16-bit spooler access and implemented 32-bit spooler APIs.
