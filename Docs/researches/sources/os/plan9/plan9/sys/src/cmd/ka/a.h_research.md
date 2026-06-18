# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/a.h

This is the SPARC assembler shared header for `ka`. It includes Plan 9 libc/Bio and `../kc/k.out.h`, then defines assembler data structures, global state, constants, and function prototypes.

Core structures are `Sym` for symbols/macros, `Io` for nested input streams, `Gen` for parsed operands, and `Hist` for source history. It defines assembler constants such as `NSYMB`, `HISTSZ`, `NHUNK`, `NHASH`, `STRINGSZ`, and input macros like `GETC()`.

The global state covers debug flags, include paths, macro definitions, symbol hash table, source history, current PC, pass number, output buffer, input stack, and active token values.

It also declares the shared compiler compatibility layer APIs from `../cc/compat.c`, making the assembler portable across Plan 9, Unix, and Windows build hosts.
