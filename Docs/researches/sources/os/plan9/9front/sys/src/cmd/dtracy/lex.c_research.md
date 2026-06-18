# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/lex.c

This file implements lexical analysis, symbol-table management, AST node construction, type formatting, and primitive type interning for dtracy scripts.

Key responsibilities:
- Tokenizes script strings from memory, including comments, identifiers, probe-name fragments with `:`, numeric literals, string literals, keywords, and multi-character operators.
- Tracks line numbers and error counts.
- Builds AST nodes through `node`.
- Maintains a global symbol table using an FNV-style hash.
- Formats node kinds and types for diagnostics/debug output.
- Provides canonical integer and string types through `type`.

Important implementation notes:
- Keywords and operators are stored in sorted tables with first-character indexes.
- String escapes support common C-style escapes but not octal/hex escapes.
- Identifiers accept bytes `>= 0x80`, matching Plan 9’s UTF-oriented conventions.
- Pointer type interning in `mkptr` searches `typereg`, but the created pointer type is not linked back into `typereg`; pointer support appears incomplete or unused.
