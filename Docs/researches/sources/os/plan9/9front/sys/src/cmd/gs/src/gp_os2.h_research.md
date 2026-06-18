# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.h

OS/2 platform support header.

Key contents:
- Include guard `gp_os2_INCLUDED`.
- Includes OS/2 API headers with spooler and windowing feature macros enabled.
- Declares `HWND hwndtext` for DLL builds.
- Declares `pm_find_queue` and `pm_spool`, implemented in `gp_os2.c`.

Research notes:
- This header exposes printer queue/spooling helpers used by OS/2 printer IODevice code.
