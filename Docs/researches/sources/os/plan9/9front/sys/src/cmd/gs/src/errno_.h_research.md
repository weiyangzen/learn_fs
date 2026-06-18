# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/errno_.h

## Scope

Portable wrapper around system `errno.h`.

## Key Behavior

- Includes Ghostscript `std.h` before system headers.
- Includes `<errno.h>`.
- Declares `extern int errno` if `errno` was not provided as a macro.

## Dependencies

Depends on Ghostscript portability header `std.h` and the platform C library `errno.h`.

## Risks And Invariants

- Exists for old environments where `<errno.h>` defines error constants but does not declare `errno`.
- The `extern int errno` fallback must not conflict with platforms where `errno` is thread-local macro state.
