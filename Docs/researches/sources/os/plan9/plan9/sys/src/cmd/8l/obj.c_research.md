# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/obj.c

Purpose: 386 linker entry point, command-line setup, object/archive loader, symbol table, profiling instrumentation, and dynamic import/export setup.

Key behavior: `main` parses header/output/library/profiling/dynamic flags, sets default memory layout, loads objects/libraries, runs passes, and emits output. `objfile` loads files or archive members; `ldobj` decodes Plan 9 object records, symbols, history, data, text, floating literals, and branch offsets. Helpers manage autolibs, history paths, arena objects, symbols, profiling insertion, endian tables, IEEE conversion, imports, exports, and undefineds.

Integration notes: decodes object format emitted by `8c/swt.c`; produces `Prog` and `Sym` streams consumed by `pass.c`, `span.c`, and `asm.c`. Dynamic module support uses `SIMPORT`, `SEXPORT`, `SUNDEF`, relocation indexes, and generated `_exporttab`.
