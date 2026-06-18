# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/parser.y

Bison parser and parse-state implementation for the GFS2 metadata language.

Grammar:
- Script is semicolon-separated statements.
- Statements: `set <blockspec> [<typespec>] { field: value, ... }` and `get <blockspec> [state]`.
- Block specs can be offsets, numeric addresses, paths, identifiers, or subscripts.
- Field values can be numbers or strings.

Public APIs implemented:
- `lgfs2_lang_init()`
- `lgfs2_lang_free()`
- `lgfs2_lang_parsef()`
- `lgfs2_lang_parses()`

Behavior:
- Builds linked AST statement lists using `ast_left`.
- Uses `ast_right` for statement operands and field/value chains.
- Initializes line number to 1.
- `lgfs2_lang_parses()` duplicates input, wraps it with `fmemopen()`, parses, and treats parser or lexer error state as failure.

Risk notes:
- AST shape is positional and tightly coupled to `lang.c`.
- Field list links are constructed through `ast_left`, so traversal order follows parser construction.
- `lgfs2_lang_free()` assumes `state` and `*state` are non-null.
- Parser is pure/reentrant but AST and result handling remain manually managed.
