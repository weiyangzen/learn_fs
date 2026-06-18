# File Research: sources/os/bsd/netbsd-src/lib/libc/misc/Makefile.inc

Read completely: 15 lines.

This makefile fragment adds miscellaneous libc sources. It optionally includes `ubsan.c` when `MKLIBCSANITIZER=yes`, and always includes constructor startup support `initfini.c` and stack protector support `stack_protector.c`.

Important interactions: uses architecture and generic misc paths through `.PATH`.

Security/reliability notes: no runtime behavior. The selected files affect process initialization and compiler-inserted stack/bounds failure handling.
