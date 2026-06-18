# File Research: sources/os/bsd/freebsd-src/sys/sys/stack.h

## Purpose
`stack.h` declares kernel stack capture, storage, printing, and tracing interfaces.

## Main Interfaces
- Exposes `struct stack` operations: create, destroy, put, copy, zero, print, compact/long sbuf formatting, and DDB-specific printing.
- `enum stack_sbuf_fmt` selects no formatting, long formatting, or compact formatting.
- `stack_save()` and `stack_save_td()` capture machine-dependent stack traces for the current or specified thread.
- `CTRSTACK()` logs captured stacks to KTR when KTR support is enabled.

## Implementation Notes
The header separates machine-independent stack manipulation from machine-dependent capture routines. If `sys/malloc.h` was included first, it declares `M_STACK`.

## Dependencies and Constraints
Includes `sys/_stack.h`. Forward-declares `struct sbuf` and `struct thread`. KTR support depends on `KTR` build configuration.
