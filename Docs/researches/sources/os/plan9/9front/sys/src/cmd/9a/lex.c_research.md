# File Research: sources/os/plan9/9front/sys/src/cmd/9a/lex.c

Main program, keyword table, object writer, and lexer integration for the PowerPC64 assembler `9a`.

Key contents:
- `main` configures target `thechar='9'`, `thestring="power64"`, handles `-o`, `-D`, and `-I`, and can assemble multiple files in parallel on non-Windows systems using `NPROC`.
- `assemble` derives output file names, configures include paths, creates output, runs two assembler passes, emits history on pass 2, and writes final `AEND`.
- Large `itab[]` maps assembler mnemonics, registers, special registers, condition registers, pseudo-ops, and 64-bit PowerPC instructions to parser tokens and opcode enum values.
- `cinit` initializes null operands, symbol table, keyword symbols, input state, and working directory path.
- `zname` and `zaddr` serialize symbol names and operands into Plan 9 object format, including 64-bit constants, string constants, and IEEE floating constants.
- `outcode` and `outgcode` write two-operand and three-operand instruction records, manage symbol slots, line numbers, scheduler flags, and PC advancement.
- `outhist` emits file history records as `ANAME`/`AHISTORY`.
- Pulls in shared lexer, macro processor, and compatibility bodies from `../cc`.

Filesystem relevance: indirect. It emits object files used to build 9front binaries.
