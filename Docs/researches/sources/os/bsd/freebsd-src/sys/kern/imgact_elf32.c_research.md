# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_elf32.c

## Summary
Build wrapper that instantiates `kern/imgact_elf.c` for 32-bit ELF.

## Main Contents
Defines `__ELF_WORD_SIZE 32` and includes `<kern/imgact_elf.c>`.

## Important Behavior
All ELF loader/core-dump logic comes from the shared `imgact_elf.c` template, with macros resolving to 32-bit ELF types and symbol names.

## Risks
This file has no independent runtime logic. Its risk is compile-time configuration: it must be included only in builds that need the 32-bit ELF image activator.
