# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fscanf.c

Read completely: 78 lines.

This file implements `fscanf` and `fscanf_l`. Both collect variadic arguments and call `__svfscanf` or `__svfscanf_l`.

Important interactions: thin public wrappers around the scanf engine.

Security/reliability notes: format parsing, locale behavior, and input error handling are delegated.
