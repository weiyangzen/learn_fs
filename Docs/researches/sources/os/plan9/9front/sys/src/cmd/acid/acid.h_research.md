# File Research: sources/os/plan9/9front/sys/src/cmd/acid/acid.h

Central declarations, global state, data structures, and opcode definitions for the Acid debugger language.

Key contents:
- Defines interpreter limits, value types, format checking, and AST opcodes.
- Declares global debugger/interpreter state: maps, process table, symbol hash, IO stack state, current executable, GC state, return context, flags, and output buffers.
- Defines `Type`, `Frtype`, `Ptab`, `Rplace`, `Gc`, `Store`, `List`, `Value`, `Lsym`, `Node`, and `String`.
- Declares parser, evaluator, memory access, debugger process control, symbol, list, GC, module, and formatting functions.

Role:
- Shared ABI for the Acid parser, evaluator, builtins, lexer, list support, and main program.

Notable risks:
- The interpreter stores many mutable globals; reentrancy is not a design goal.
- `Store` is reused in `Node`, `List`, and `Value`, so type/fmt fields must stay coherent.
