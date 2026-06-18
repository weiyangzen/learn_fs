# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/Makefile.inc

## Scope

AArch64 compatibility architecture build fragment.

## Behavior

- Includes `${COMPATARCHDIR}/sys/Makefile.inc`.

## Dependencies And Invariants

- No gen or locale compatibility sources are added here; AArch64 compatibility work in this group is under `sys`.
