# File Research: sources/os/plan9/9front/sys/src/cmd/qa/lex.c

Power/PowerPC assembler front-end for `qa`. It sets `thechar='q'`, initializes assembler symbols and instruction/register names, runs a two-pass assembly over `.s` input, and writes Plan 9 object records.

Key responsibilities:
- `main` parses `-o`, `-D`, `-I`, supports parallel multi-file assembly via `NPROC`, and blocks multi-file assembly on Windows.
- `assemble` sets include paths, output name, pass 1/pass 2 parsing, preprocessor definitions, and history emission.
- `itab` maps Power register names, condition registers, special registers, directives, and opcodes to parser token classes and opcode values.
- `zname`, `zaddr`, `outcode`, and `outgcode` serialize symbols, operands, two-operand instructions, and three-operand/fused instructions to object output.
- `outhist` emits source history/path metadata, including Windows path handling.

Dependencies and coupling:
- Includes `a.h`, `y.tab.h`, and shared compiler bodies `../cc/lexbody`, `../cc/macbody`, `../cc/compat`.
- Uses opcode/address constants from the Power assembler/linker world.
- Shares object encoding conventions with `qc/swt.c`.

Filesystem/OS relevance:
- Mostly toolchain code, but directly handles pathnames, include search paths, output object creation, and source history records used by Plan 9 tools.
