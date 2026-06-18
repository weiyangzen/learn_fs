# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.h

Conditional include and external-declaration header shared by `postio.c` and `ifdef.c`.

Contents:
- Includes system terminal headers based on `SYSV`, `V9`, `BSD4_2`, `DKHOST`, and `DKSTREAMS`.
- Declares V9 `tty_ld`.
- Provides BSD `FD_ZERO` and `FD_SET` macros and `errno` declaration.
- Includes Datakit headers and declares Datakit helpers when `DKHOST` is enabled.
- Declares `postio.c` globals needed by `ifdef.c`: printer line, tty descriptors, log file, message buffer, baud/stop settings, interactive flag, process role flags, and read/write permissions.

Role:
- Keeps platform-dependent build branches centralized so `postio.c` can call `setupline()`, `resetline()`, `setupstdin()`, and `readline()` without direct system-header clutter.

Risks and quirks:
- Exposes many globals across translation units.
- BSD `FD_*` macros are simplistic integer bitset definitions rather than modern `fd_set` use.
- Build correctness depends on exactly one expected platform macro being defined by `postio.mk`.
