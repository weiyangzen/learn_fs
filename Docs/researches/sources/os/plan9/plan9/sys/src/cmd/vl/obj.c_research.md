# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/obj.c

Main driver, option parser, object/archive loader, symbol manager, profiling injector, and endian/floating helper code for the Plan 9 MIPS linker `vl`.

Key responsibilities:
- Parses linker flags, selects output profile/header type, creates the output file, and runs the linker pipeline: `patch`, profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, `undef`.
- Supports big-endian `v.out` and little-endian `0.out` mode.
- Loads plain Plan 9 object files and Plan 9 archives, including symbol-table-driven archive member extraction for unresolved externals.
- Decodes object records into `Prog`, `Adr`, `Sym`, `Auto`, history, data, global, dynamic, init, and text state.
- Tracks autolibs through `AHISTORY`, expands `$O`/`$M`, and searches configured lib directories.
- Interns symbols by name/version, allocates linker hunks, and creates `Prog` nodes.
- Converts floating constants into data literals for `AMOVF`/`AMOVD`.
- Adds optional profiling or embedded tracing calls.

Important behavior:
- Default entry is `_main` or `_mainp` unless overridden with `-E`.
- `-H` supports several MIPS output layouts: Unix simple, Plan 9, boot images, COFF, ELF, 64-bit ELF, and headerless.
- Duplicate `TEXT` can be skipped when marked `DUPOK`.
- `ASUB`/`ASUBU` constants are canonicalized into negative adds.
- Errors remove the partial output file.

Risks:
- Parser assumes trusted Plan 9 object/archive layout and uses fixed-size buffers.
- Archive loading loops until no unresolved symbols are satisfied, so symbol-state corruption can cascade.
