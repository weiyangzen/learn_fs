# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsio.h

Header that forbids direct use of standard input/output/error and selected stdio convenience functions.

Behavior:
- Undefines and redefines `stdin`, `stdout`, and `stderr` to unavailable symbols.
- Redefines functions like `getchar`, `printf`, `puts`, `scanf`, and related calls to unavailable expressions.

Purpose:
- Forces the library and interpreter to route I/O through Ghostscript’s redirected IODevice/stream mechanisms instead of process-global stdio.
