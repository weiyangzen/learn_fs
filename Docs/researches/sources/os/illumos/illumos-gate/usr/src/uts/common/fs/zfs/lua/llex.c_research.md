# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.c

## Role

`llex.c` implements Lua's lexical analyzer. It reads a `ZIO` input stream and produces parser tokens with semantic values for names, strings, and numbers.

## Main Responsibilities

- Initializes and fixes reserved-word strings.
- Converts tokens to printable strings for diagnostics.
- Maintains a growable scanner buffer with overflow checks.
- Reports lexical and syntax errors with chunk IDs and line numbers.
- Interns scanned strings and anchors them in the active function table during compilation.
- Tracks line numbers and handles all Lua newline combinations.
- Sets lexer input state, source name, environment-name string, decimal point, lookahead token, and scanner buffer.
- Reads decimal and hexadecimal numerals, with locale decimal-point retry.
- Reads long strings/comments with `[=*[` delimiters.
- Reads short strings and escapes, including simple escapes, hex escapes, decimal escapes, escaped newlines, and `\z` whitespace skipping.
- Tokenizes comments, operators, punctuation, reserved words, identifiers, strings, numbers, and EOF.
- Provides one-token lookahead.

## Integration Points

The parser drives this file through `luaX_next` and `luaX_lookahead`. It depends on `lctype`, `lobject`, `lstring`, `ltable`, `lzio`, and `ldo` for classification, interned strings, dynamic buffers, and syntax errors.

## Risk Notes

Lexer risks include buffer growth limits, long-string delimiter matching, numeric locale behavior, escape validation, and line-number overflow. String anchoring prevents GC from collecting tokens during parsing.
