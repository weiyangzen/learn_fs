# File Research: sources/os/bsd/freebsd-src/sbin/restore/main.c

Purpose: program entry point, global option state definition, argument parsing, and top-level mode orchestration for `restore`.

Key behavior:
- Defines global flags such as `bflag`, `dflag`, `Dflag`, `hflag`, `mflag`, `Nflag`, `uflag`, `vflag`, `yflag`, `command`, `dumpnum`, `volno`, maps, times, and `terminal`.
- Parses modern options with `getopt()` and converts obsolete compact restore syntax through `obsolete()`.
- Selects exactly one command mode: interactive `i`, resume `R`, full/incremental restore `r`, table/list `t`, or extract `x`.
- Calls `setinput()`, `setup()`, `extractdirs()`, `initsymtable()`, and the relevant high-level restore workflow.
- `usage()` prints mode-specific command forms and exits through `done()`.

Integration: this file sequences the entire restore pipeline. It decides when to initialize from an existing checkpoint symbol table, when to scan directories, when to build extraction lists, and when to checkpoint again.

Risk notes: the program is intentionally global-state heavy; command sequencing is critical. Resume mode relies on `restoresymtable` being consistent with the current tape. Obsolete argument rewriting allocates new argv strings and exits on malformed legacy syntax.
