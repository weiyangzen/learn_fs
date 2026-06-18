# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/obj.c

Main driver and object/archive loader for the PowerPC Plan 9 linker.

Major responsibilities:
- Defines linker identity: `thechar='q'`, `thestring="power"`, default output `q.out`.
- Parses options for output, entry, text/data addresses, header type, library paths, exports, imports, dynamic modules, and debug flags.
- Sets executable header defaults for boot, Be boot, Plan 9, raw, XCOFF, and ELF variants.
- Initializes global linker state, opcode tables, byte-order maps, symbol state, object list, and output file.
- Orchestrates the full pass pipeline:
  `objfile/loadlib -> import/export -> patch -> profiling -> dodata -> follow -> noops -> span -> asmb -> undef`.

Object loading:
- `objfile()` loads regular object files or Plan 9 archives.
- Archive loading reads the symbol table and repeatedly pulls archive members for unresolved `SXREF` symbols.
- `ldobj()` decodes object records, symbol/name records, history records, data records, text records, floating constants, globals, dynamic tables, and branch/data operands.
- `zaddr()` decodes serialized operands and records auto/param metadata.
- `addlib()` resolves autolib history paths, expanding `$O` and `$M`, deduplicating libraries.

Symbol/memory management:
- `lookup()` hashes symbols by name and version.
- `prg()` allocates initialized `Prog` nodes from hunks.
- `gethunk()` grows linker arena memory.
- `nuxiinit()` computes byte-order maps.

Instrumentation/dynamic support:
- `doprof1()` inserts counter data and increment sequences.
- `doprof2()` inserts calls to `_profin/_profout` or tracing hooks.
- `undefsym()`, `zerosig()`, and `readundefs()` support import/export lists and dynamic modules.

Risk/notes:
- `ldobj()` is the format-critical path; malformed object records can desynchronize parsing.
- Static symbols use object-version scoping.
- Duplicate `TEXT` can be skipped under `DUPOK`, otherwise diagnosed.
- Dynamic-loadable module mode changes layout assumptions (`HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, entry).
