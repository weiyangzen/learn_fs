# File Research: sources/os/bsd/netbsd-src/lib/libutil/efun.c

## Purpose
Provides error-checking convenience wrappers for allocation, string, file, formatting, and numeric conversion operations.

## Key Details
- Default error handler is `err`; `esetfunc` can replace it.
- Wrappers include `emalloc`, `ecalloc`, `erealloc`, `ereallocarr`, `estrdup`, `estrndup`, `estrlcpy`, `estrlcat`, `efopen`, `easprintf`, `evasprintf`, `estrtoi`, and `estrtou`.
- On failure, wrappers call the configured error function, generally exiting or otherwise aborting caller flow.

## Dependencies and Role
- Generic libutil support code, useful for command-line utilities that prefer fail-fast allocation and conversion handling.
