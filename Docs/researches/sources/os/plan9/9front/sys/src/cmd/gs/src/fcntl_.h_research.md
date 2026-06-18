# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fcntl_.h

## Scope

Portable wrapper for `open` flag constants.

## Key Behavior

- Includes Ghostscript `std.h` before `<fcntl.h>`.
- Maps Microsoft `_O_*` constants to standard `O_*` names when missing.

## Dependencies

Depends on platform `<fcntl.h>` and Ghostscript portability conventions.

## Risks And Invariants

- Exists because some Microsoft C environments omit standard `O_*` names.
- Only aliases a fixed set of flags: append, binary, create, exclusive, read-only, read-write, truncate, and write-only.
