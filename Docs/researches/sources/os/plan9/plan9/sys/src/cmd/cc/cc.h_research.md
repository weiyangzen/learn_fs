# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/cc.h

Central shared header for the Plan 9 C compiler. It defines AST `Node`, symbol `Sym`, declaration `Decl`, type `Type`, input/history structures, bitsets, enums for AST ops, type codes, storage classes, type flags, ABI targets, and global compiler state.

It declares compiler-wide tables for type compatibility, names, type categories, signatures, and machine widths, plus globals for lexer/parser state, declarations, include paths, output buffers, current function, debug flags, and configuration flags.

The prototype set covers platform compatibility, parser/lexer, macro processing, declarations, semantic/type processing, constant evaluation, function declarations, subtree utilities, Acid/pickle/debug output, bitsets, varargs/pragma checking, machine code generation hooks, 64-bit emulation rewrites, and machine capability checks.
