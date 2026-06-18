# File Research: sources/os/plan9/9front/sys/src/cmd/2a/lex.c

Purpose: driver, symbol/opcode initialization, and object emission for the 68020 assembler `2a`.

Key behavior:
- `main()` handles flags, include paths, `-D` defines, output selection, and parallel multi-file assembly on non-Windows systems using `NPROC`.
- `assemble()` performs two passes: pass 1 parses and resolves labels; pass 2 emits history records and object code.
- `itab[]` maps register names, special registers, width suffixes, and every assembler mnemonic to parser token class and `2.out.h` opcode.
- `cinit()` initializes `nullgen`, hash table, special symbols, opcode/register symbols, and working directory state.
- `zname()`, `zaddr()`, and `outcode()` serialize names, addresses, and instructions into Plan 9 object format with compact symbol-cache slots.
- `outhist()` writes path/history records, including Windows drive/path handling.
- Includes common `../cc/lexbody`, `../cc/macbody`, and `../cc/compat` for lexical scanning and preprocessor-like macro behavior.

Research notes:
- `outcode()` increments assembler `pc` for all non-`AGLOBL`/`ADATA` records during both passes.
- Address serialization mirrors compiler output in `2c/swt.c`, making hand assembly and compiler output link-compatible.
- FPU constants are converted through `ieeedtod()` into simulated IEEE fields.
