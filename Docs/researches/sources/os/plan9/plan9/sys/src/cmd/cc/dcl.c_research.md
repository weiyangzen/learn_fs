# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/dcl.c

This file implements declaration, type layout, initializer, prototype, enum, tag, label, and symbol-scope handling for the shared Plan 9 C compiler.

Key behavior:
- Builds declarator types from parser nodes in `dodecl()`, including arrays, pointers, functions, and bitfields.
- Expands aggregate initializers with `doinit()`, `init1()`, `peekinit()`, and `nextinit()`, including string-to-array expansion and auto-initializer assignment trees.
- Computes struct/union layout in `sualign()`, including bitfield packing and calls into Acid/pickle debug output hooks.
- Manages old-style and ANSI function prototypes with `fnproto()`, `fnproto1()`, `walkparam()`, and `argmark()`.
- Maintains declaration stack rollback with `markdcl()`, `push1()`, and `revertdcl()`, including unused local/parameter warnings and volatile-use emission.
- Checks type equivalence and type signatures with `sametype()`, `rsametype()`, `signature()`, and `sign()`.
- Handles struct/union tags, labels, parameter conversion, auto/global/parameter declarations, type merging, struct element declarations, and enum constants.

Important details:
- Incomplete arrays in typedefs are copied so per-variable array widths can diverge from the typedef.
- `CLOCAL` static locals are rewritten to private static symbols via `mkstatic()`.
- Structure layout also triggers `acidtype()` and `pickletype()` side effects for debug/introspection output.
- `contig()` attempts a specialized zero-fill loop for large contiguous automatic objects after initialization.

Filesystem relevance:
- Indirect. This is compiler infrastructure used to build Plan 9 software, not filesystem code itself.
