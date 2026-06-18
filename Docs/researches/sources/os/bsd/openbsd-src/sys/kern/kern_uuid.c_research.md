# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_uuid.c

Read completely: 119 lines.

Contains minimal kernel UUID formatting support and documentation for UUID octet layout. In this OpenBSD version the file defines only debug-only print helpers plus a private layout structure; the encode/decode section is represented by comments but no non-debug encode/decode functions are implemented in the file.

Key contents:
- `struct uuid_private` describes UUID fields as time-low, time-mid, time-hi, sequence, and node words for formatting.
- Under `DEBUG`, `uuid_snprintf()` formats a UUID into canonical hexadecimal groups, converting sequence and node words from big endian.
- Under `DEBUG`, `uuid_printf()` prints the formatted UUID via `printf()`.
- The final comment documents the RFC/DCE UUID octet layout with time, clock sequence, and node fields.

Dependencies and notes:
- Includes `sys/endian.h` for `betoh16()`, `sys/systm.h` for `snprintf()`/`printf()`, and `sys/uuid.h` for public UUID constants and types.
- There is no allocation, locking, parsing, generation, or syscall/sysctl surface in this file.
