# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/funopen.c

Read completely: 173 lines.

This file implements `funopen2` and compatibility `funopen` for custom stream backends. `funopen2` installs caller-provided read/write/seek/flush/close hooks directly; `funopen` wraps older `int`-sized callbacks in adapters that clamp large transfer sizes and free the adapter cookie on close.

Important interactions: custom-cookie stream creation used by memory and application-defined streams.

Security/reliability notes: `funopen`'s write adapter loops across large writes but relies on callbacks making progress; a zero-byte successful write would be problematic.
