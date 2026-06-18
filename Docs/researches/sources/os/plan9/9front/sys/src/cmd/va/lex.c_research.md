# File Research: sources/os/plan9/9front/sys/src/cmd/va/lex.c

`lex.c` is the main driver, symbol initializer, object emitter, and lexer/preprocessor integrator for the `va` MIPS assembler. It parses command-line flags, handles multiple input files in parallel where supported, runs two assembly passes, emits history/name/address/object records, initializes register/instruction symbols, and includes shared compiler lexer and macro bodies.

The instruction table maps textual registers, special registers, floating registers, and opcodes to yacc token classes and architecture opcodes. `outcode()` emits object records only on pass 2, interns symbols in a bounded table, and increments `pc` for non-DATA/GLOBL instructions.

The file relies on Plan 9 compiler compatibility routines for filesystem, process, include, macro, and lexical behavior. It is the executable core around the grammar in `a.y`.
