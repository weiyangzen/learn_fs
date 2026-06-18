# File Research: sources/os/plan9/9front/sys/src/cmd/7a/lex.c

- Role: Main program, symbol/instruction table, initialization, and object-output support for the ARM64 assembler `7a`.
- `main()` parses assembler options, supports `-o`, `-D`, `-I`, and parallel assembly of multiple files using `NPROC` on non-Windows systems.
- `assemble()` selects output name, configures include paths, opens the output, runs the assembler in two passes, emits history on pass 2, applies command-line defines each pass, and flushes output.
- Large `itab[]` initializes built-in symbols: register aliases, SP/SB/FP/PC names, general/floating/vector registers, system registers, condition codes, extension suffixes, barrier/system names, and ARM64 mnemonics mapped to parser token classes and opcode constants.
- `cinit()` initializes `nullgen`, clears errors/input stacks/hash table, interns built-ins, and records current working directory for history output.
- `syminit()` initializes new symbols as unresolved names.
- `cclean()` emits final `AEND` and flushes the object file.
- `zname()` and `zaddr()` serialize symbols and ARM64 operands to Plan 9 object format, including 64-bit constants, OREG/pre/post/branch/shift/ext/register-offset operands, string constants, and IEEE float constants.
- `outsim()`, `outcode()`, and `outcode4()` maintain the small symbol cache and emit two- or three-operand object records; pass 1 advances `pc` without output.
- `outhist()` emits file history records with path splitting and Windows path handling.
- Ends by including shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`, so lexer, macro processor, include handling, and compatibility functions are shared with other Plan 9 toolchain components.
