# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/lex.c

Lexer and directive handler for `eqn`.

Key behavior:
- Tokenizes equation input, quoted strings, contiguous identifiers, spaces, thin spaces, braces, keywords, and inline delimiters.
- Expands user definitions from `deftbl`, including macro calls with arguments.
- Handles directives: `define`, `tdefine`, `ndefine`, `ifdef`, `delim`, `gsize`, `gfont`, `include`/`copy`, and `space`.
- `include()` opens an input file with `fopen()`, pushes it onto the input stack, and emits `.lf` line directives.
- `delim()` configures inline equation delimiters.

Filesystem relevance:
- Directly opens include/copy files for nested equation input.
