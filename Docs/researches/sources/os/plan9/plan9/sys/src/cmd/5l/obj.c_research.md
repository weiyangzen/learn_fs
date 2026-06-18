# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/obj.c

## Scope

Main driver, object/archive reader, symbol table, profiling insertion, endian setup, and import/export support for `5l`.

## Behavior

- Parses linker options for output, entry, library paths, text/data addresses, head type, export table, and DLM import mode.
- Loads object files and archives, resolves autolibs, builds symbol and program lists, then runs linker passes: patch, profiling, data layout, flow ordering, noops, span, assembly, undefined checks.
- `ldobj()` reads Plan 9 object streams, handles `ANAME`/`ASIGNAME`, history, text/data/global/dynamic records, branch offsets, floating constants, and duplicate symbols.
- `lookup()` manages versioned symbols in a fixed hash table.
- `gethunk()` grows arena memory.
- `doprof1()`/`doprof2()` inject profiling or tracing instrumentation.
- `nuxiinit()` sets byte-order tables; `ieeedtof()`/`ieeedtod()` convert floating encodings.
- `readundefs()`, `import()`, and `export()` support dynamic module import/export metadata.

## Dependencies

Uses Plan 9 `ar.h`, `l.h`, object format constants, archive format constants, and host filesystem access for objects and libraries.

## Risks And Invariants

- `zaddr()` allocates `sizeof(Ieee)` but subtracts `NSNAME` from `nhunk` for `D_FCONST`, which looks inconsistent.
- Object parsing assumes bounded records and uses fixed read-buffer refill logic.
- Archive symbol-table parsing trusts old Plan 9 archive layout.
- The custom arena allocator means `free()` calls are no-ops under `compat.c`.
