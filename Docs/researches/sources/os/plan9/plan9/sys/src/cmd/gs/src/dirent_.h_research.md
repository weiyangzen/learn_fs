# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dirent_.h

## Purpose

`dirent_.h` is a Ghostscript portability wrapper for directory-entry headers. It gives the rest of the codebase a single `dir_entry` type regardless of whether the platform exposes POSIX `struct dirent` or older `struct direct` headers.

## Behavior

- Includes `std.h` before any platform header that may include `sys/types.h`.
- Includes `gconfig_.h`, where the build system defines header-availability switches.
- If `HAVE_DIRENT_H` is defined, includes `<dirent.h>` and aliases `struct dirent` to `dir_entry`.
- Otherwise conditionally includes `<sys/dir.h>`, `<sys/ndir.h>`, and/or `<ndir.h>`, then aliases `struct direct` to `dir_entry`.

## Dependencies / Interfaces

- Depends on build-time feature macros from `gconfig_.h`.
- Exports only one public compatibility typedef: `dir_entry`.

## Filesystem Relevance

This is filesystem-adjacent portability infrastructure: it abstracts directory enumeration structure names for Ghostscript code that scans directories. It does not itself open directories, read entries, or implement filesystem behavior.

## Research Notes

The header is intentionally narrow. Its correctness depends entirely on configure/makefile detection setting exactly the right `HAVE_*` macros for the target platform.
