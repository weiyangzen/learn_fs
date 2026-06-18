# File Research: sources/os/plan9/9front/sys/src/cmd/6l/obj.c

- Role: Main program and object/archive reader for the amd64 linker.
- `main()` parses options, configures header defaults, initializes opcode index, operand-class coverage, register maps, buffers, defaults, and pipeline state, then loads objects/libraries and runs linker passes through `asmb()`.
- Supports Plan 9 output defaults, dynamically loadable module mode, export table generation, profiling/tracing insertion, and alternate entry/header/text/data/rounding options.
- `objfile()` loads raw object files or archives; archive loading reads the symbol table and pulls members only for unresolved external references.
- `ldobj()` decodes Plan 9 object records, handles `ANAME`/`ASIGNAME`, histories/autolibs, `ATEXT`, `AGLOBL`, `ADATA`, dynamic import/export pseudo-ops, float literal pooling, branch PC adjustment, duplicate `DUPOK` text skipping, and mode changes.
- `zaddr()` decodes compact serialized operands from object files and builds auto/param metadata for stack symbols.
- Symbol and program allocation helpers: `lookup()`, `prg()`, `copyp()`, and `appendp()`.
- Profiling helpers `doprof1()` and `doprof2()` inject counter or call-based profiling/tracing code.
- Endianness/float helpers include `nuxiinit()`, `find1()`, `find1v()`, `find2()`, `ieeedtof()`, and `ieeedtod()`.
- Import/export helpers: `undefsym()`, `zerosig()`, and `readundefs()`.
