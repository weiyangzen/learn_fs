# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/acid.h

Core shared declarations for the Acid debugger interpreter.

Key contents:
- Defines global interpreter state, execution flags, maps, symbols, process ids, IO stack state, and parser state.
- Defines operation codes, type tags, and format metadata.
- Defines `Type`, `Frtype`, `Ptab`, `Rplace`, `Gc`, `Store`, `List`, `Value`, `Lsym`, `Node`, and `String`.
- Declares expression, list, symbol, process, module, type, memory-indirection, debugger, lexer, parser, and GC functions.
- Defines the `expr(n,r)` dispatch macro over `expop`.

Dependencies:
- Built around Plan 9 libmach concepts: `Map`, `Symbol`, registers, process control, and executable text maps.
- Shared by parser, lexer, evaluator, builtins, and main program.

Notable risks:
- Many globals are declared through the `Extern` macro pattern.
- Node/list/string lifetime is managed by a custom mark/sweep GC.
