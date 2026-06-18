# File Research: sources/os/plan9/9front/sys/src/cmd/8l/obj.c

Main driver and object/archive loader for the Plan 9 386 linker `8l`.

Key contents:
- `main` parses linker flags, selects executable header format, initializes opcode lookup/operand class coverage/register maps, reads object files, loads libraries, patches control flow, lays out data/text, optionally injects profiling, spans instructions, initializes data relocations, assembles output, and checks undefined symbols.
- Supports Plan 9, COFF-like Unix, old “garbage unix”, DOS `.COM`, fake DOS `.EXE`, and ELF header presets.
- `isobjfile` distinguishes object/archive inputs for option parsing around import/export lists.
- `loadlib` repeatedly scans autolibraries until unresolved external references stop being resolved.
- `objfile` handles plain object files and Plan 9 archive symbol tables, loading only archive members needed by unresolved symbols.
- `ldobj` decodes `.8` object records, symbol/name records, history records, text/data/global pseudo-ops, dynamic import/export records, branch offsets, and floating constants materialized into data symbols.
- `zaddr` decodes serialized object operands and collects auto/param metadata for symbol tables.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` manage Plan 9 file-history/autolib records.
- `doprof1` and `doprof2` insert simple counter profiling or `profin/profout` calls.
- `nuxiinit`, `ieeedtof`, and `ieeedtod` support host byte order and floating constant conversion.
- `readundefs`, `import`, `export`, and helpers implement dynamically loadable module import/export metadata.

Filesystem relevance: indirect build infrastructure. It consumes and emits binary/object files and libraries but does not implement filesystem semantics.
