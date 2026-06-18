# File Research: sources/os/bsd/netbsd-src/lib/libutil/logwtmpx.c

## Purpose
Appends a `wtmpx` record.

## Key Details
- Initializes a `struct utmpx`.
- Copies line, user, host, type, exit status, signal, and timestamp.
- Calls `updwtmpx(_PATH_WTMPX, &ut)`.

## Dependencies and Role
- Extended login history writer.
