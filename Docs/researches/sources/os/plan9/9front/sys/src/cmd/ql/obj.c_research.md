# File Research: sources/os/plan9/9front/sys/src/cmd/ql/obj.c

This file is the main program and object/archive loader for the `ql` PowerPC linker.

Key responsibilities:
- `main()` parses linker options, initializes output format defaults, opens the output file, loads object files, resolves libraries, performs all linker passes, and emits the final binary.
- Supports output selection for boot, Be PEF, Plan 9, raw, XCOFF, and ELF variants.
- Handles `-x` export-table and `-u` dynamically loadable module modes.
- `objfile()` loads either plain object files or Plan 9 archives with symbol headers.
- `ldobj()` parses Plan 9 object records, builds `Prog` chains, resolves `ANAME`/`ASIGNAME`, handles history/autolib metadata, `TEXT`, `GLOBL`, `DATA`, `DYNT`, and `INIT`.
- Floating constants in `FMOVS`/`FMOVD` are interned as generated data symbols.
- `loadlib()` repeatedly loads autolibs until external references stop being resolved.
- `doprof1()` and `doprof2()` inject profiling/tracing code.
- `lookup()` manages the linker symbol hash table.

Important support:
- `zaddr()` decodes serialized object addresses and records auto/param symbols.
- `addlib()`, `addhist()`, `histtoauto()`, and `collapsefrog()` process object history and autolib paths.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` handle target endian layout and IEEE conversions.
- `readundefs()` reads explicit import/export symbol lists.

Implementation notes:
- Duplicate `TEXT` with `DUPOK` is skipped by turning instructions into NOPs.
- Undefined dynamic imports become `SUNDEF` with relocation index encoding.
