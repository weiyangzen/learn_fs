# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genman

Shell generator for `terminfo.5` manual capability tables.

Key responsibilities:
- Reads:
  - `terminfo.5.in`
  - `term.h`
  - `termcap_map.c`
- Extracts long capability names, terminfo codes, termcap codes, and descriptions.
- Replaces placeholders:
  - `@BOOLCAPS@`
  - `@NUMCAPS@`
  - `@STRCAPS@`

Role in subsystem:
- Ensures the manual page’s capability tables are generated from the same capability definitions used by runtime code.
