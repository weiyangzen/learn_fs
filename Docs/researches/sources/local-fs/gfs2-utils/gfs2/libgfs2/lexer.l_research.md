# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lexer.l

Flex lexer for the GFS2 metadata language.

Recognized tokens:
- Punctuation: `{}`, `[]`, comma, colon, semicolon.
- Keywords: `set`, `get`, `state`.
- Values: decimal/hex numbers, signed offsets, identifiers, single-quoted strings, single-quoted absolute paths.
- Comments: `//...` and `#...`.
- Whitespace/newlines with line/column tracking.

Behavior:
- Allocates AST nodes directly for meaningful tokens via `ast_new()`.
- Stores lexer extra data as `struct lgfs2_lang_state *`.
- Increments `ls_linenum` and resets `ls_colnum` on newline/comment.
- Strips surrounding quotes for strings and paths before creating AST nodes.

Integration role:
- Emits tokens used by `parser.y`.
- Uses bison bridge/reentrant scanner mode.

Risk notes:
- `]` returns a token carrying an `AST_EX_SUBSCRIPT` node, which parser actions depend on.
- Unexpected characters print using `yylineno`, while line tracking otherwise uses custom state fields.
- String/path escaping is minimal and later unescaped by interpreter code.
