# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/obj.c

Read fully: 1379 lines, 23646 bytes. SHA-256 prefix: `917b12c34dcad30f`.

This is the main driver and object/archive loader for the SPARC linker. `main()` parses options, initializes header defaults, library paths, output file, instruction table, symbol state, endian tables, and the initial program list. It loads input objects and libraries, then runs the full linker pipeline: `patch()`, optional profiling insertion, `dodata()`, `follow()`, `noops()`, `span()`, `asmb()`, and `undef()`.

Core components:
- `objfile()` loads regular object files or Plan 9 archives, resolving archive members through the `__.SYMDEF` index and unresolved `SXREF` symbols.
- `ldobj()` decodes `.k` object records, including `ANAME`, `AHISTORY`, `AGLOBL`, `ADATA`, `ADYNT`, `AINIT`, `ATEXT`, and normal instructions.
- `zaddr()` decodes serialized operands and records auto/param metadata.
- `addlib()` interprets history records for autolib paths, replacing `$O` and `$M`.
- `lookup()`, `prg()`, and `gethunk()` allocate symbols and program nodes from linker hunks.
- `doprof1()` and `doprof2()` inject profiling/tracing instrumentation.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` support target byte order and floating constants.

Integration: this file owns the lifecycle of the linker’s global state and supplies allocation and symbol lookup for all other `kl` passes.

Risk notes: archive loading loops until no new xrefs resolve. Object parsing is byte-oriented and treats malformed records as fatal. Duplicate `TEXT` handling respects `DUPOK` by turning skipped code into nops.
