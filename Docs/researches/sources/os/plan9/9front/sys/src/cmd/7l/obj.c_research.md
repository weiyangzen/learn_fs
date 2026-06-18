# File Research: sources/os/plan9/9front/sys/src/cmd/7l/obj.c

Main ARM64 linker driver, object/archive reader, symbol table manager, profiling inserter, and floating/endian helper code.

Key entry points:
- `main` parses linker options, chooses output/header layout, initializes linker state, loads object files and libraries, optionally builds import/export tables, then runs `patch`, profiling, `dodata`, `follow`, `noops`, `span`, and `asmb`.
- `usage` and `errorexit` handle command-line and error exits.
- `objfile` loads either a raw object or Plan 9 archive, resolving archive members from the archive symbol table.
- `ldobj` decodes Plan 9 object records into `Prog` nodes, handles symbol/name records, history records, data records, text records, branch offsets, duplicate text handling, and floating literal synthesis.

Object/symbol helpers:
- `isobjfile` distinguishes object/archive input from import/export symbol-list files.
- `zaddr` decodes serialized operand records into `Adr`.
- `lookup` hashes and interns symbols by name/version.
- `prg` allocates and initializes a `Prog`.
- `nopout` rewrites an instruction to `ANOP`.
- `readsome` refills the object input buffer while preserving unconsumed bytes.
- `addlib`, `addhist`, `histtoauto`, and `collapsefrog` maintain history/autolib metadata from `AHISTORY`.

Pipeline and rewrite details:
- Negative immediate `ADD`/`SUB` variants are canonicalized to the opposite operation.
- Non-encodable float constants for `AFMOVS`/`AFMOVD` are moved into synthetic data literals.
- `AGLOBL`, `ADATA`, `ADYNT`, and `AINIT` are diverted into data lists.
- `ATEXT` establishes text symbols, PC values, frame sizes, and text-chain links.
- Branch operands are adjusted by the current object base PC.
- Archive loading loops while unresolved `SXREF` symbols can pull in more members.

Profiling helpers:
- `doprof1` creates `__mcount` data and inserts counter increments at function entry.
- `doprof2` inserts calls to `_profin`/`_profout` or `_tracein`/`_traceout`.

Other helpers:
- `nuxiinit`/`find1` initialize byte-order conversion tables.
- `ieeedtof` converts Plan 9 double representation to single precision.
- `ieeedtod` converts Plan 9 IEEE representation to host `double`.

Filesystem relevance: indirect. This is OS toolchain infrastructure for producing ARM64 Plan 9 binaries.
