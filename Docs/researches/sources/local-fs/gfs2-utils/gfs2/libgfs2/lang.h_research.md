# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.h

Header for the GFS2 metadata language.

Defines:
- `struct lgfs2_lang_state`: parser/interpreter cursor and error location state.
- `struct lgfs2_lang_result`: block number, block buffer, metadata type, or bitmap state.
- `ast_node_t`: statement, expression, and keyword node types.
- AST interpreter status constants.
- `struct ast_node`: binary AST node with text/string/numeric payloads.
- `YYSTYPE` as `struct ast_node *` for bison/flex integration.

Exports:
- Language init/parse/result/free APIs.
- AST allocation/destruction APIs.
- `ast_type_string[]`.

Risk notes:
- This header couples parser, lexer, interpreter, and libgfs2 metadata definitions.
- AST ownership is manual and recursive.
- C++-style `//` comments appear in a C header; build mode must tolerate them.
