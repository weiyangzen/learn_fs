# File Research: sources/os/bsd/dragonflybsd/sys/sys/times.h

Process CPU accounting structure and `times(3)` declaration.

Key contents:
- Ensures `clock_t` is declared.
- Defines `struct tms`:
  - user CPU time
  - system CPU time
  - terminated children user CPU time
  - terminated children system CPU time
- Userland-only declaration:
  - `clock_t times(struct tms *)`

Research notes:
- This is standard POSIX process accounting ABI.
- Kernel builds receive only the type definitions, not the libc prototype.
