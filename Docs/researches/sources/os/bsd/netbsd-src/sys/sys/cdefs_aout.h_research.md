# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs_aout.h

## Scope

Provides a.out object-format support macros for symbol labels, aliases, warnings, IDs, copyright strings, and link sets.

## APIs And Behavior

- Defines C symbol labels with leading underscore.
- Implements `___RENAME`, strong/weak aliases, weak extern/reference support, and warning references using assembler directives/stabs where supported.
- Defines `__IDSTRING`, `__RCSID`, `__COPYRIGHT`, and kernel ID/copyright macros.
- Implements a.out link set entries with stabs records and declares link set structure containing length and item array.
- Provides link set start, end, and count macros.

## Dependencies

- Included by `cdefs.h` on non-ELF builds.

## Risks And Invariants

- Assembler syntax differs by compiler and standard mode; macros contain legacy K&R branches.
- Link set layout differs from ELF and includes an explicit length field.
