# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/cc.y

Yacc grammar for the Plan 9 C compiler frontend. It parses external declarations, function definitions, declarators, parameter declarations, struct/union/enum bodies, initializers, blocks, statements, labels, expressions, type names, storage classes, and qualifiers.

Semantic actions construct `Node` trees with `new`, manage declarations through `dodecl`, `markdcl`, `revertdcl`, `argmark`, `pdecl`, `adecl`, and `xdecl`, and call `codgen` for completed functions unless Acid/debug modes suppress codegen.

The grammar supports Plan 9 extensions such as `signof`, `used`, `set`, type strings, compound structure constructors, anonymous generated tags, and `...` prototypes. It also handles string literal concatenation for byte and wide/rune strings.
