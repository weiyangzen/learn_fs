# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/Makefile.inc

## Scope

i386 compatibility architecture build fragment.

## Behavior

- Includes i386 compatibility syscall sources.
- Also participates in i386-specific compatibility source selection for old runtime ABI support.

## Dependencies And Invariants

- Depends on i386 `SYS.h`, assembly ABI, and selected compatibility gen/sys fragments.
