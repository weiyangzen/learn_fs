<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parser_lex.l -->
# sources/test-tools/filebench/parser_lex.l

Purpose: defines the flex lexer for Filebench WML. It tokenizes commands, entity names, attributes, random-variable keywords, literals, variables, quoted strings, punctuation, comments, and whitespace.

Important APIs/functions: returns tokens declared in `parser_gram.y`, fills `yylval` fields for integers, booleans, strings, variables, and quoted string fragments, tracks `lex_lineno`, reports syntax errors through `yyerror()`, and exposes `yy_switchfileparent()`/`yy_switchfilescript()` buffer helpers.

Control flow: in `INITIAL` state it ignores spaces/tabs/comments, increments line count, recognizes keywords before generic strings, parses numeric suffixes `k`, `m`, `g` into byte-scaled integers, and enters `WHITESTRINGSTATE` on quotes. Quoted strings are returned as a sequence of `FSV_WHITESTRING` or variable tokens until the closing quote.

State/persistence: global `lex_lineno` persists for diagnostics. Flex buffer globals `parent` and `script` support switching input buffers. The lexer allocates token strings with `strdup()`; parser callbacks convert them into AVD/string storage.

Dependencies/integration: includes `filebench.h`, parser types, generated grammar header, and utility macros such as `KB`, `MB`, `GB`. Calls `filebench_shutdown()` on allocation failure.

Risks: token rules are order-sensitive; new keywords must precede generic string matching. Variable and string regexes are restrictive and may reject valid-looking paths or names. Numeric scaling can overflow before `errno` catches all cases because multiplication happens after conversion. Quoted-string handling has several special cases for `$`, backslash, and newline escapes that need regression coverage.

Test signals: lexer tests for every keyword, comments, line numbers, quoted strings with variables and escaped newline/dollar, integer suffixes, negative integers, booleans, path-like strings, illegal characters, and parser buffer switching.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parser_lex.l -->
