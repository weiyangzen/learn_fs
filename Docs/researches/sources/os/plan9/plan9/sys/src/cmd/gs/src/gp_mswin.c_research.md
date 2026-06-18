# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.c

Read status: complete.

Purpose: Microsoft Windows platform support for Ghostscript, mainly legacy printer spooling, temporary files, process pipes, and lifecycle/cache stubs.

Main logic:
- Defines global DLL/application state: `phInstance`, `is_win32s`, `szAppName`, and `win_prntmp`.
- Lifecycle functions are minimal; `gp_do_exit` calls `exit`.
- Persistent cache functions are stubs.
- `gp_open_printer` detects printer targets and writes to a scratch spool file, handles pipe targets with `popen`, otherwise opens normal files.
- `gp_close_printer` sends scratch output to the selected printer and deletes the temporary file.
- `is_spool` recognizes `\\spool` pseudo-prefixes.
- `is_printer` treats empty names, `win.ini` ports, and `\\spool` names as printers.
- `gp_printfile` chooses Win32 spooler APIs or the legacy `gs16spl.exe` path depending on Win32s and target syntax.
- `get_queues`, `get_ports`, `get_queuename`, and `get_portname` enumerate/select printer queues or ports, including dialogs and `FILE:` save selection.
- `gp_printfile_win32` copies a temporary file to a printer using `OpenPrinter`, `StartDocPrinter`, `WritePrinter`, `EndDocPrinter`, and `ClosePrinter`.
- `gp_printfile_gs16spl` launches `gs16spl.exe` for Win32s/Win16-style spooling.
- `mswin_popen` implements a write-only binary pipe to a child process using inheritable handles and `CreateProcess`.
- `gp_open_scratch_file` uses temp directory discovery, `GetTempFileName`, `CreateFile`, `_open_osfhandle`, and `fdopen`.
- `gp_fopen` delegates to `fopen`.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides Windows scratch-file creation, pipe-backed process output, printer pseudo-files, and ordinary file open behavior.
- This is a major platform file-device support implementation.

Notable behavior and risks:
- Contains legacy Win32s and `win.ini` support.
- Uses several fixed-size buffers and string concatenation.
- Temporary printer output is staged through a global filename, not thread-safe.
