# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.c

OS/2 and EMX/GCC platform support, with DOS fallback paths.

Key behavior:
- Provides error strings, realtime/usertime via `gettimeofday`, and console detection.
- Defines OS/2/DOS filename constants, binary modes, null device, and current directory.
- Enumerates files with `DosFindFirst`/`DosFindNext` on OS/2; DOS fallback returns the pattern once.
- Initializes EMX DLL environment from the process environment and installs a SIGFPE handler.
- Opens printers as OS/2 spool scratch files, pipes, `PRN`, or normal files.
- Finds and validates spool queues with `SplEnumQueue`.
- Spools scratch-file data through `SplQmOpen`, `SplQmStartDoc`, `SplQmWrite`, and `SplQmEndDoc`.
- Creates scratch files with `_tempnam` for IBM C or `mktemp`/`gp_fopentemp` otherwise.
- Implements Windows/DOS-like path-combination helpers.
- Stubs persistent cache and native font enumeration.

Notable dependencies:
- OS/2 spooler and DOS APIs, EMX support, `gdevpm.h`, and `gp_os2.h`.

Research notes:
- `\\spool\queue` is the OS/2 queue naming convention for printer output.
- Comments warn that user CPU time is approximated by realtime.
