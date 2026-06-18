# File Research: sources/os/bsd/freebsd-src/sys/sys/procfs.h

Read completely: 120 lines.

## Purpose
Defines procfs/core-dump debugger structures used to expose register and process information to debuggers, especially ELF core consumers.

## Main Elements
- Typedefs machine register sets as `gregset_t`, `fpregset_t`, `prgregset_t`, and `prfpregset_t`.
- Defines stable `prstatus_t` with version, structure/register sizes, OS release, current signal, thread id, and general registers.
- Defines `prpsinfo_t` with version, command name, arguments, and process id.
- Defines `thrmisc_t` for thread name notes and `psaddr_t` for target addresses.
- Provides 32-bit compatibility structures when `__HAVE_REG32` is present.

## Dependencies And Integration
Used by procfs, core dump generation, debuggers, machine register definitions, and 32-bit compatibility core note emission.

## Risk Notes
The file explicitly warns not to change or remove existing structure fields. These layouts are debugger/core-file ABI and must remain backward compatible.
