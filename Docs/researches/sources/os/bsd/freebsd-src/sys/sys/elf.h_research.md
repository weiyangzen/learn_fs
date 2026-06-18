# File Research: sources/os/bsd/freebsd-src/sys/sys/elf.h

## Purpose
Solaris-compatible umbrella header for ELF definitions.

## Main Elements
- Includes `sys/types.h`, machine-specific ELF definitions, `sys/elf32.h`, and `sys/elf64.h`.

## Dependencies And Integration
Used by code expecting `<sys/elf.h>` to provide both class-independent and class-specific ELF types.

## Risk Notes
Actual machine relocation and ABI constants come from `machine/elf.h` and common ELF headers, not this wrapper.
