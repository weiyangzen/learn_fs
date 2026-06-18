# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.c

Microsoft Windows platform support for Ghostscript DLL builds.

Key behavior:
- Provides basic init/exit/termination hooks and unimplemented persistent cache stubs.
- Opens printer destinations by writing to a scratch file first, then spooling it on close.
- Detects printer names from empty output names, win.ini `[ports]`, or `\\spool` prefixes.
- Enumerates printer queues/ports and prompts through dialog boxes when needed.
- Spools via Win32 `OpenPrinter`/`StartDocPrinter`/`WritePrinter` for Win95/NT-class systems.
- Falls back to launching `gs16spl.exe` for Win32s or port-style printing.
- Implements a custom write-only `mswin_popen` using `CreatePipe`, inheritable handles, and `CreateProcess`.
- Creates scratch files using `GetTempPath`, `GetTempFileName`, `CreateFile`, `_open_osfhandle`, and `fdopen`.
- Provides plain `fopen` as `gp_fopen`.
- Stubs native font enumeration.

Notable dependencies:
- Windows shell/spooler APIs and shared declarations from `gp_mswin.h`.
- Path helpers from `gpmisc.h`.

Research notes:
- Printing behavior preserves legacy `\\spool\...` semantics while newer `%printer%` support lives in `gp_msprn.c`.
- The custom `popen` only supports mode `wb`.
