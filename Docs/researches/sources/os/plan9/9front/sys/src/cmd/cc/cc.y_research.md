# File Research: sources/os/plan9/9front/sys/src/cmd/cc/cc.y

Purpose: Yacc grammar for the Plan 9 C compiler front end.

Key points:
- Defines semantic value union for AST nodes, symbols, types, specs, strings, floats, and integers.
- Declares tokens for C keywords, constants, strings, operators, type names, qualifiers, Plan 9 extensions, and varargs.
- Parses external declarations, function definitions, automatic declarations, parameter declarations, struct/union fields, abstract declarators, initializers, labels, statements, expressions, casts, calls, member access, strings, aggregate bodies, enum declarations, and type/class/qualifier lists.
- Builds AST nodes using `new`.
- Uses declaration helpers such as `dodecl`, `doinit`, `markdcl`, `revertdcl`, `argmark`, `fndecls`, `dotag`, and `doenum`.
- Supports extensions including case ranges, compound literals/constructors, `used`, `set`, `signof`, unnamed parameters, and `...`.

Dependencies and interactions:
- Includes `cc.h`.
- Consumes lexer tokens from the compiler lexer.
- Produces trees consumed by semantic analysis in `com.c` and declarations in `dcl.c`.
- Function definitions call `codgen` unless Acid/pickle debug modes suppress code generation.

Research notes:
- The grammar encodes both syntax and early semantic actions, especially declaration scoping and type construction.
- Function bodies are wrapped with declaration-stack marks so local symbols can be reverted and unused diagnostics emitted.
