# File Research: sources/os/plan9/9front/sys/src/cmd/tl/obj.c

`obj.c` is the `tl` linker driver and object/archive loader.

Driver flow:
- `main()` parses flags, selects output format, initializes tables/state, opens output, loads objects, loads libraries, handles import/export mode, and runs phases:
  `patch`, profiling, `reachable`, `dodata`, `fnptrs`, `follow`, `noops`, `span`, `asmb`, `undef`.
- Supports `-o`, `-E`, `-T`, `-D`, `-R`, `-H`, `-x`, `-u`, and debug-letter flags.
- Defaults output to `5.out`.

Object/archive loading:
- `isobjfile()` distinguishes object/archive inputs for option parsing.
- `objfile()` handles `-l` library names, regular object files, and Plan 9 archives.
- `loadlib()` repeatedly loads autolibs until unresolved externs stop changing.
- `ldobj()` decodes Plan 9 ARM object records, names, signatures, history, text/data directives, float constants, and branch offsets.
- `zaddr()` decodes serialized `Adr` operands and records autos/params.

Symbol/data helpers:
- `lookup()` interns symbols by name/version.
- `prg()` allocates initialized `Prog` records.
- `addhist()`, `histtoauto()`, `collapsefrog()`, `addlib()` manage history/autolib metadata.
- `nopout()` rewrites skipped duplicate text into NOP.
- `nuxiinit()`, `ieeedtof()`, `ieeedtod()` handle endian and floating conversions.
- `readundefs()` reads import/export symbol lists.

Profiling:
- `doprof1()` injects counter increments into text.
- `doprof2()` injects `_profin` and `_profout` calls.

Risk notes:
- Object decoding is tightly coupled to Plan 9 `.5` object encoding.
- Archive symbol table format is assumed; stale archives trigger diagnostics.
- Duplicate `TEXT` with `DUPOK` is skipped by NOPing instructions.
