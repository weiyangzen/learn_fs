# File Research: sources/os/plan9/9front/sys/src/cmd/1a/lex.c

Main program, opcode table, initialization, and object writer for `1a`.

Key responsibilities:
- Parses command-line options `-o`, `-D`, `-I`, debug flags, and supports parallel assembly of multiple files on non-Windows systems.
- Runs two assembler passes in `assemble`, initializing include paths, preprocessing defines, parsing, and writing final object output.
- Defines `itab`, mapping reserved names, registers, special registers, and all 68000/68881 mnemonics to parser token classes and opcode values.
- Initializes the symbol table, default `nullgen`, target identifiers `thechar='1'`, `thestring="68000"`, and working directory state.
- Serializes object names, addresses, instructions, and file history records with `zname`, `zaddr`, `outcode`, and `outhist`.
- Includes shared compiler lexer, macro, and compatibility bodies from `../cc`.

Notable details:
- Object encoding uses compact bit flags such as `T_FIELD`, `T_INDEX`, `T_OFFSET`, `T_SYM`, `T_FCONST`, `T_SCONST`, and `T_TYPE`.
- `outcode` increments assembler `pc` for real instructions but not for `AGLOBL` and `ADATA`.
