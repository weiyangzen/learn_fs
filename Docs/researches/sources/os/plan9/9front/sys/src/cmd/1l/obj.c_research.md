# File Research: sources/os/plan9/9front/sys/src/cmd/1l/obj.c

Main program, object/archive loader, autolib handling, profiling insertion, symbol table, and numeric/float conversion support for `1l`.

Key responsibilities:
- Parses linker flags for output, entry, header type, text/data bases, alignment, and debug modes.
- Sets default target identity `thechar='1'`, `thestring="68000"` and default Plan 9 output settings.
- Initializes special/simple addressing tables, output file, symbol table, and required helper symbols `_mull`, `_divsl`, `_divul`, and `_ccr`.
- Loads object files and archives, including archive symbol table lookup and iterative library extraction for unresolved `SXREF`s.
- `ldobj` parses Plan 9 object records, name/signature records, histories, text/data/global records, branch references, auto/param metadata, and instruction streams.
- Performs early canonicalizations: `JSR`/`BSR`, quick immediates, add/sub sign flips, quick shifts, address-register compare/clear tweaks, and float-constant-to-integer opcode substitutions.
- Tracks source history and autolib paths through `histfrog`, `addhist`, `addlib`, and `histtoauto`.
- Supports optional profiling/tracing instrumentation with `doprof1` and `doprof2`.
- Provides symbol lookup/allocation, program allocation/copying, endian map initialization, and IEEE double/single conversion.

Notable details:
- Archive loading repeatedly scans libraries until no new unresolved symbols are resolved.
- Static symbols use the object-file `version` to avoid collisions.
