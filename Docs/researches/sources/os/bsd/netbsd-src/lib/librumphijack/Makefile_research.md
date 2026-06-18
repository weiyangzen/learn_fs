# File Research: sources/os/bsd/netbsd-src/lib/librumphijack/Makefile

Read completely: 25 lines.

Builds `librumphijack`, the preload/interposition library that redirects host calls through rumpclient. It disables full RELRO, static library generation, and profiling for dynamic-function use, depends on `libpthread` and `librumpclient`, and installs the `rumphijack.3` manual.

Sources are `hijack.c` and `hijackdlsym.c`. The build defines `_DIAGNOSTIC` and `_REENTRANT`, uses warning level 5, forces `hijackdlsym.c` to `-O0` so stack-frame assumptions hold, and undefines `_FORTIFY_SOURCE`.
