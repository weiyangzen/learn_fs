# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/lex.c

Lexer and input stack for the Acid language.

Key responsibilities:
- Initializes keyword table.
- Pushes files or strings as lexer input sources.
- Restarts and pops IO sources.
- Formats symbols through `%L`.
- Provides character pushback, escaped-character decoding, string scanning, newline/comment handling, and tokenization.
- Parses identifiers, numbers, format suffixes, strings, and reserved words.
- Maintains the Acid symbol table with `enter`, `look`, and `mkvar`.

Dependencies:
- Uses Bio for file input, y.tab token definitions, Acid string/node helpers, and global parser state.

Notable risks:
- Lexer state is global and stacked manually.
- Number/symbol parsing is integrated with Acid’s format suffix syntax.
