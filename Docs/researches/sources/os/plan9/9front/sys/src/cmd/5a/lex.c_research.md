# File Research: sources/os/plan9/9front/sys/src/cmd/5a/lex.c

This file is the ARM assembler driver, opcode/register table, initialization, and object-code emitter for `5a`.

Main flow:
- `main()` sets `thechar='5'`, `thestring="arm"`, initializes globals, parses `-o`, `-D`, `-I`, and `-t` options, and assembles one or more files.
- On non-Windows systems, multiple input files are assembled in parallel up to `$NPROC`.
- `assemble()` derives the output file name, sets include paths, opens the output object, runs the parser twice, emits history between passes, and finalizes with `cclean()`.

Instruction table:
- `itab[]` defines special names (`SP`, `SB`, `FP`, `PC`), integer registers `R0`-`R15`, floating registers `F0`-`F15`, coprocessor regs `C0`-`C15`, `CPSR`/`SPSR`, FP control regs, condition suffixes, address-mode suffixes, and all ARM assembler mnemonics supported by this tool.
- Includes LDREX/STREX, long exclusive forms, barriers, long multiply forms, VFP/FPA-style floating ops, and Plan 9 pseudo ops.

Object emission:
- `cinit()` initializes `nullgen`, clears symbol hash, installs `itab[]`, and records current path.
- `zname()` writes an `ANAME` record.
- `zaddr()` writes encoded operands, including integer offsets, string constants, and IEEE double constants.
- `outcode()` performs pass-sensitive emission, interns from/to symbols into the rolling `h[NSYM]` object symbol cache, writes opcode/condition/register/line and operands, and increments `pc` for real instructions.
- For `AB` with condition suffixes, `outcode()` rewrites to the corresponding conditional branch opcode.
- `outhist()` emits path components and `AHISTORY` records for debug history.

Dependencies and interactions:
- Includes yacc output `y.tab.h` and common lexer/macro bodies from `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.
- Emits the object format consumed by ARM linker tooling and shares constants with `5c/5.out.h`.

Research relevance:
- This is the operational heart of `5a`: command-line behavior, keyword set, two-pass parse strategy, and serialized object format.

Risk notes:
- The object symbol cache wraps through `NSYM`; collision handling uses a `jackpot` retry when from/to share the same slot.
- `assemble()` mutates `outfile` globally, so multi-file behavior depends on fork isolation.
- The Windows path logic and history path splitting are special-cased.
