# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fsetpos.c

Read completely: 70 lines.

This file implements `fsetpos`. It restores saved wide-character conversion state when wide mode is active, then seeks to the stored `fpos_t` byte offset using `fseeko`.

Important interactions: pair for `fgetpos`.

Security/reliability notes: failure behavior is delegated to `fseeko`; invalid `fpos_t` values can fail as invalid seeks.
