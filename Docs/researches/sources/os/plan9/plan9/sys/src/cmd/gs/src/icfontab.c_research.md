# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icfontab.c

Defines the compiled-font procedure table. It includes generated `gconfigf.h` twice:
- First to declare extern compiled font procedures.
- Second to populate `fprocs[]`.

Exports `ccfont_fprocs`, returning the procedure count, table pointer, and `ccfont_version` for compatibility checking.
