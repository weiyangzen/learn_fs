# File Research: sources/os/plan9/9front/sys/src/cmd/8a/lex.c

This file is the main driver, opcode/register table, initialization, and object emitter for the 386 assembler.

Key responsibilities:
- `main()` parses `-o`, `-D`, `-I`, debug flags, and supports parallel assembly of multiple files on non-Windows hosts using `NPROC`.
- `assemble()` runs the assembler in two passes: pass 1 resolves labels and pc counts, pass 2 writes history and object records.
- `itab[]` defines assembler names for pseudo-registers, x86 general registers, FPU/MMX/XMM registers, segment/control/debug/task registers, instruction mnemonics, aliases, x87 ops, conditional moves, MMX/SSE instructions, and pseudo-ops.
- `cinit()` initializes null operands, IO state, hash table, predefined symbols, and current working directory.
- `zname()`, `zaddr()`, `outcode()`, and `outhist()` write Plan 9 object records with compact symbol caching and source-history records.
- Includes shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat` for lexical scanning, macro processing, and host compatibility.

Integration points:
- Consumes grammar from `a.y`.
- Emits object format defined by `8.out.h`.
- Shares source history encoding conventions with `8c/swt.c`.

Risks and invariants:
- The symbol cache is limited by `NSYM` and wraps from slot 1.
- `outfile` is global and mutated from input filename; multi-file assembly uses child processes to isolate state.
- Object encoding depends on `Gen` fields being consistently initialized to `nullgen`.
