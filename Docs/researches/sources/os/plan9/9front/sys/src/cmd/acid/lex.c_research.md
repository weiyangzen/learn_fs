# File Research: sources/os/plan9/9front/sys/src/cmd/acid/lex.c

Lexer, keyword table, input stack, string/file input management, symbol table insertion/lookup, and source-location formatting for Acid.

Key responsibilities:
- Registers reserved words through `kinit()`.
- Manages nested input sources from files and strings with `pushfile()`, `pushstr()`, `popio()`, and `restartio()`.
- Formats source stack locations with `%L`.
- Lexes strings, escapes, comments, numbers, identifiers, operators, character constants, format suffixes, and interactive newlines.
- Maintains line numbers and interactive brace stacking.
- Stores identifiers and keywords in a hash table of `Lsym`.

Important behavior:
- `//` comments are consumed through newline.
- Interactive newlines produce `;` unless inside braces.
- Numeric lexer supports binary `0b`, hex `0x`, floats, and ordinary integer constants.
- Identifiers allow `_`, `$`, alnum, and UTF-ish bytes above `~`.
- New symbols are initialized as unset integer values with default `X` format.

Dependencies:
- Uses Plan 9 `bio`, global parser `yylval`, Acid hash table, and error handling.

Notable risks:
- Numeric scanning accepts `-` and `+` inside floats broadly after float mode, which is permissive.
- `popio()` deliberately refuses to pop the base input and restarts it instead.
