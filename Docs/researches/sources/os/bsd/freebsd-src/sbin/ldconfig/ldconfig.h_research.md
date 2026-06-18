# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.h

## Purpose
Declares the shared interface between `ldconfig.c` and `elfhints.c`.

## Contents
- Include guard `LDCONFIG_H`.
- Includes `<stdbool.h>`.
- Declares global `bool insecure`, controlled by the `-i` flag.
- Declares:
  - `void list_elf_hints(const char *);`
  - `void update_elf_hints(const char *, int, char **, bool, bool);`

## Integration Points
This header is included by both the CLI driver and ELF hints implementation.
