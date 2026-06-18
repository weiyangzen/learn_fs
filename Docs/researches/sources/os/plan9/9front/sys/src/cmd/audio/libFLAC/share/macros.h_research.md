# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/macros.h

## Role

`share/macros.h` defines `FLAC_CHECK_RETURN()`, a shared diagnostic macro for checking unlikely system-call failures.

## Contents

The macro evaluates an expression, and if the result is negative, prints the expression text and `strerror(errno)` to `stderr`.

## Important Notes

The file comments acknowledge that libraries ideally should not print directly, but this macro is intended for operations that are extremely unlikely to fail, such as restoring a saved owner/group.

## Risks / Edge Cases

- The macro uses `fprintf()`, `strerror()`, and `errno` but the header only includes `<errno.h>`; callers must have declarations for stdio/string functions in scope.
- It evaluates the expression once.
- Direct stderr output from library code can surprise embedders.

## Dependencies

Includes `<errno.h>` and relies on surrounding includes for `fprintf`, `stderr`, and `strerror`.
