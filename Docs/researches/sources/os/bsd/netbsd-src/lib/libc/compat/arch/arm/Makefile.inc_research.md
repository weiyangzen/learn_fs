# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/Makefile.inc

## Scope

ARM compatibility architecture build fragment.

## Behavior

- Includes the ARM compatibility syscall make fragment.

## Dependencies And Invariants

- All listed ARM compatibility files are selected through `arch/arm/sys/Makefile.inc`.
