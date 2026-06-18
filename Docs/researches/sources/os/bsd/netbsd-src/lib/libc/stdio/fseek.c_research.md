# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fseek.c

Read completely: 66 lines.

This file implements `fseek` as a `long` offset wrapper around `fseeko`. It converts the input offset to `off_t` and delegates all logic.

Important interactions: legacy API shim over the large-file-aware seek implementation.

Security/reliability notes: a commented-out unsigned `SEEK_SET` conversion documents an intentionally rejected compatibility behavior.
