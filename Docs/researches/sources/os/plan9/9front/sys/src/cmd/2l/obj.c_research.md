# File Research: sources/os/plan9/9front/sys/src/cmd/2l/obj.c

Purpose: main linker driver, object/archive loader, symbol table manager, autolibrary resolver, profiling injection, byte-order setup, and float conversion.

Key behavior:
- `main()` parses linker flags, selects header defaults, validates `optab`, initializes address-mode tables, creates output, loads objects/libraries, then runs link phases: `patch()`, optional profiling, `follow()`, `dodata()`, `dostkoff()`, `span()`, `asmb()`, and `undef()`.
- `loadlib()` repeatedly scans autolibraries until no unresolved `SXREF` symbols are resolved.
- `objfile()` handles direct object files and Plan 9 archives with `__.SYMDEF` symbol indexes, loading only archive members needed for unresolved symbols.
- `zaddr()` decodes serialized object addresses, including fast compact formats and full tagged formats, and records auto/param minima for current function.
- `addlib()` reconstructs autolibrary paths from encoded history components, expanding `$O` and `$M`.
- `addhist()`, `histtoauto()`, and `collapsefrog()` manage file-history records and path component overflow.
- `ldobj()` reads `.2` object streams, handles `ANAME`/`ASIGNAME`, history, end records, globals, data, text, branches, quick immediates, constant arithmetic normalization, shift quicks, address-register compare/clear tweaks, and FPU immediate-to-integer substitutions.
- `lookup()` maintains hash table symbols keyed by name plus static version.
- `doprof1()` injects `__mcount` counter increments and data records; `doprof2()` injects calls to `_profin/_profout` or tracing variants.
- `nuxiinit()`, `find1()`, `find2()`, `ieeedtof()`, and `ieeedtod()` define host-to-target byte order and floating conversions.

Research notes:
- Static symbols use incrementing `version` so same-name statics from different object files remain distinct.
- Object load phase already performs target-specific instruction canonicalization before later span/encoding.
- Autolib references are encoded as `AHISTORY` records with offset `-1`.
