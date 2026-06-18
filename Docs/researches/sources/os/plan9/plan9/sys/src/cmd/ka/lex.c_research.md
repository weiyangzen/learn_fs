# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/lex.c

This file is the main driver, keyword table, object writer, and shared lexer integration for the SPARC assembler. It sets `thechar='k'` and `thestring="sparc"`.

`main()` parses assembler flags, supports `-o`, `-D`, `-I`, runs multiple input files in parallel using `NPROC` on non-Windows hosts, and calls `assemble()`. `assemble()` derives output names, configures include paths, creates the output file, runs pass 1 and pass 2, emits history, and flushes output.

`itab[]` maps register names, special registers, coprocessor registers, floating registers, opcodes, pseudo-ops, and scheduler controls to yacc token classes and opcode values. This table is the assembler’s lexical instruction set.

`zname()`, `zaddr()`, `outcode()`, and `outhist()` serialize Plan 9 object records. The file includes shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`, so macro processing and cross-host compatibility are inherited from the common compiler frontend.
