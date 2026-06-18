# sources/test-tools/cthon04/special/fstat.c

## Purpose
prints total and free file-node counts from `statfs`/`statvfs` for a path, validating filesystem statfs availability.

## Important APIs, Types, and Functions
`main()` selects `struct statfs` or `struct statvfs` and calls `statfs()`, SVR3 `statfs(name,&fs,sizeof,0)`, or `statvfs()`.

## Control Flow and State
It accepts optional path, zeroes `f_files`/`f_ffree`, calls the platform API, and prints counts.

## Persistence and Dependencies
no lasting state; it only reads filesystem metadata. Dependencies: platform mount/statfs headers and `u_long` formatting.

## Integration Points, Risks, and Test Signals
Integration is the special filesystem-capacity probe. Risks are platform struct layout variation and DOS/Win skip. Signals are successful `total/free` output.
