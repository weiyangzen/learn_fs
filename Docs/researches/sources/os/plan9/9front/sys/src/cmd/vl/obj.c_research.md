# File Research: sources/os/plan9/9front/sys/src/cmd/vl/obj.c

This is the main program and Plan 9 object/archive loader for the MIPS linker.

Key behavior:
- `main` parses linker flags, selects output header defaults, initializes global state, opens output, loads object files/libraries, then runs `patch`, optional profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, and `undef`.
- `objfile` opens regular objects or Plan 9 archives and lazily loads archive members that satisfy unresolved `SXREF` symbols.
- `ldobj` decodes Plan 9 object records, symbol names, addresses, histories, globals, dynamic/init/data records, text records, branch offsets, and floating constants.
- Supports autolib path construction from history records with `$O`/`$M` expansion.
- Maintains file-history autos, local static symbol versions, duplicate-text skipping with `DUPOK`, and data records linked through `datap`.
- `doprof1` and `doprof2` inject profiling/tracing instrumentation.
- `nuxiinit`, `ieeedtof`, and `ieeedtod` provide byte-order maps and floating conversion.

Integration and risks:
- Object decoding assumes the Plan 9 compiler object format and fixed maximum record sizes.
- Archive loading loops until unresolved symbols stop being resolved; incorrect `SXREF` state can affect library inclusion.
- Profiling insertion mutates instruction streams before scheduling/span.
