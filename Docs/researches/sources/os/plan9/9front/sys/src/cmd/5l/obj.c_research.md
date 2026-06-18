# File Research: sources/os/plan9/9front/sys/src/cmd/5l/obj.c

This file contains `5l` program startup, command-line handling, object/archive loading, symbol-table management, autolib resolution, profiling insertion, endian initialization, IEEE conversion, and import/export seed handling.

Key elements:
- `main()` parses linker flags, chooses output format/header defaults, initializes global state, loads objects and libraries, then runs the linker pipeline: `patch()`, profiling, `dodata()`, `follow()`, `noops()`, `span()`, `asmb()`, `undef()`.
- `isobjfile()` distinguishes regular object files from archives or other files.
- `loadlib()` repeatedly loads queued autolibraries until no unresolved references are resolved.
- `objfile()` opens a regular object or archive. Archive mode reads `__.SYMDEF`, scans unresolved symbols, and loads only needed members.
- `ldobj()` decodes Plan 9 ARM object records, including `ANAME`, `ASIGNAME`, `AHISTORY`, `AEND`, `AGLOBL`, `ADYNT`, `AINIT`, `ADATA`, `ATEXT`, and normal instructions.
- `zaddr()` decodes serialized operands and registers auto/param symbols for current text.
- `addlib()` expands `$O`/`$M` in autolib paths and queues unique libraries.
- `addhist()`, `histtoauto()`, and `collapsefrog()` preserve source history path metadata.
- `lookup()` manages linker symbols in a versioned hash table.
- `doprof1()` and `doprof2()` insert two styles of profiling/tracing instrumentation.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` handle byte order and floating conversion.
- `readundefs()` marks symbols as import/export candidates from user-provided lists.

Dependencies and integration:
- Uses Plan 9 archive format from `<ar.h>`.
- Produces `Prog` lists and `Sym` entries consumed by all later linker passes.

Notable behavior:
- Duplicate text with `DUPOK` is skipped by replacing instructions with NOPs.
- Floating constants unsupported as immediate chip floats are materialized as data literals.
- Static symbols are versioned per object to avoid name collision.
- `INITENTRY` defaults to `_main` or `_mainp` for profiling.

Research notes:
- This file is the front half and orchestration center of `5l`.
- It tightly couples Plan 9 object-stream encoding with the linker’s in-memory IR.
