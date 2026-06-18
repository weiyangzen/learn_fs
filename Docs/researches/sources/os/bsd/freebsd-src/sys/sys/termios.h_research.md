# File Research: sources/os/bsd/freebsd-src/sys/sys/termios.h

## Scope

This compatibility shim warns that including `<sys/termios.h>` is deprecated and then includes the public `<termios.h>` header.

## APIs And Constants

- Emits a GCC warning advising use of `<termios.h>` instead.
- Includes `<termios.h>` to preserve source compatibility.

## Control Flow And Integration

- There is no runtime behavior.
- The file exists to keep old include paths building while nudging users to the standards-facing header.

## Dependencies

- Depends entirely on `<termios.h>` for actual terminal I/O types, constants, and prototypes.

## Risks And Invariants

- Removing this shim would break legacy source that still includes `<sys/termios.h>`.
- The warning is guarded by `__GNUC__`, so non-GNU compilers may not emit the deprecation notice.
