# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/lex.c

Purpose: Main program, opcode table, initialization, and object emission for the PowerPC assembler.

Key behavior:
- `main` parses assembler options, supports parallel assembly for multiple files using `$NPROC`, and dispatches `assemble`.
- `assemble` determines output file, include paths, creates output, runs two parser passes, emits history and final object.
- `itab` maps register/opcode names to yacc token types and architecture opcode values.
- `cinit` initializes symbols, null generator, IO state, and reserved names.
- `zname`, `zaddr`, `outsim`, `outcode`, and `outgcode` write Plan 9 object records and operands.
- `outhist` writes file path/history records with Unix/Windows path handling.
- Includes shared compiler lexer, macro preprocessor, and compatibility bodies.

Dependencies and integration:
- Includes generated `y.tab.h`, `a.h`, `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.
- Uses PowerPC opcode constants from `q.out.h`.

Risks and notes:
- Large opcode table is the source of assembler vocabulary.
- `outfile` is global and reused; multi-file assembly forks to isolate state.
- Symbol cache wraps at `NSYM`.
