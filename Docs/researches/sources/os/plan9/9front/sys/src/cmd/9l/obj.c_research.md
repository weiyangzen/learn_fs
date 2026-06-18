# File Research: sources/os/plan9/9front/sys/src/cmd/9l/obj.c

This file is the main `9l` driver and object/archive reader. It parses command-line options, loads object files and libraries, decodes Plan 9 object records, manages symbols, inserts profiling code, and initializes endian conversion state.

Key routines:
- `main` configures output format, entry/text/data placement, dynamic module/export options, default entry symbol, object loading, library autoloading, passes, and final assembly.
- `isobjfile`, `objfile`, and `loadlib` distinguish object files from archives and autoload needed archive members based on unresolved `SXREF` symbols.
- `ldobj` decodes object records emitted by `9c`: `ANAME`, `ASIGNAME`, `AHISTORY`, `AEND`, `AGLOBL`, `ADATA`, `ADYNT`, `AINIT`, `ATEXT`, and ordinary instructions.
- `zaddr` decodes serialized `Adr` operands and records autos/params.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` maintain source history and autolib paths.
- `lookup` manages versioned symbol hash entries.
- `doprof1` and `doprof2` insert profiling instrumentation.
- `nuxiinit`, `find1`, `ieeedtof`, and `ieeedtod` set byte-order maps and float conversion helpers.
- `undefsym`, `zerosig`, and `readundefs` support dynamic imports/exports.

Important interactions:
- Drives the full pass sequence: `patch`, optional profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, and `undef`.
- Receives object format emitted by `9c/swt.c`.
- Populates `textp`, `datap`, symbol table, autolib list, and global linker settings.

Research notes:
- Supports q.out, Plan 9 64-bit, boot, raw, ELF, and bootable ELF output modes.
- Floating constants are pooled into data symbols during object loading.
- Dynamic loadable module mode changes export/import handling and later output layout.
