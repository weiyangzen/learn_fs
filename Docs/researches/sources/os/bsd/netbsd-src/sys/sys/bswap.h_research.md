# File Research: sources/os/bsd/netbsd-src/sys/sys/bswap.h

## Scope

Defines byte-swap function declarations and optimized macro wrappers for 16-, 32-, and 64-bit values.

## APIs And Behavior

- Declares `bswap16`, `bswap32`, and `bswap64`, with optional userland renaming to `__bswap16`/`__bswap32`.
- Defines constant-expression byte-swap macros for 16/32/64-bit integers.
- Uses inline software versions on architectures where compiler bswap builtins are slow.
- Allows `machine/bswap.h` to override variable implementations.
- For GCC, wraps `bswap*` names to use constant folding when possible and variable implementations otherwise.

## Dependencies

- Includes `sys/stdint.h`, `machine/bswap.h`, and cdefs declarations.

## Risks And Invariants

- Function declarations are always present so addresses can be taken.
- Macro replacement after declarations must preserve type casts and side-effect behavior.
