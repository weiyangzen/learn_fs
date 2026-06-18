# File Research: sources/os/plan9/9front/sys/src/cmd/kl/obj.c

This is the main driver and object/archive reader for the Plan 9 SPARC linker variant `kl`. It parses linker flags, selects output header mode, initializes linker globals, loads object files and libraries, runs patch/data/layout/scheduling/codegen passes, and writes `k.out` by default.

Key behavior:
- Handles `-o`, `-E`, `-T`, `-D`, `-R`, `-H`, debug flags, and default output profiles for boot, Plan 9, and JavaStation boot headers.
- `objfile()` detects regular object files versus Plan 9 archives, reads archive symbol tables, and repeatedly loads members that satisfy unresolved `SXREF` symbols.
- `ldobj()` decodes Plan 9 object records into `Prog` nodes, tracks `ANAME`/`ASIGNAME` symbol tables, handles `AHISTORY`, `ATEXT`, `ADATA`, `AGLOBL`, `ADYNT`, and `AINIT`, resolves branch offsets relative to object-local pc, and synthesizes float literal data for `AFMOVF`/`AFMOVD`.
- `lookup()` owns the linker symbol hash table with per-object static symbol versions.
- `addlib()`, `addhist()`, `histtoauto()`, and `collapsefrog()` manage history/autolib path metadata.
- `doprof1()` and `doprof2()` inject profiling/tracing instructions and data.
- `nuxiinit()`, `find1()`, `ieeedtof()`, and `ieeedtod()` provide target/endian and floating conversion helpers.

Dependencies are almost entirely through `l.h`: global linker state, opcode/register constants, `Prog`, `Adr`, `Sym`, `Auto`, `Optab`, diagnostics, and later passes. The file also depends on Plan 9 archive layout from `<ar.h>` and Bio I/O.

Notable risks: the code assumes trusted Plan 9 object/archive formats and uses fixed-size buffers plus unchecked `malloc`; malformed input usually ends in diagnostics or process exit rather than recovery. It is single-process, global-state linker code, not a reusable parser.
