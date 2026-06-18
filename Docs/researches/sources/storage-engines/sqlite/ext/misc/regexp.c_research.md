# sources/storage-engines/sqlite/ext/misc/regexp.c

Purpose: implements a bounded UTF-8 NFA regexp engine and registers `regexp(pattern,string)` plus case-insensitive `regexpi()`.

Important APIs/types/functions: `ReCompiled`, `ReInput`, and `ReStateSet` hold compiled opcodes and active NFA states. Compilation uses `re_compile()`, `re_subcompile_re()`, `re_subcompile_string()`, `re_append()`, `re_insert()`, and `re_esc_char()`. Matching uses `re_match()`. `re_sql_func()` caches compiled regexes with auxdata.

Control flow: compilation parses anchors, alternation, grouping, quantifiers, classes, escapes, and ranges into opcodes, bounded by `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` derived NFA limits. Matching advances through UTF-8 input, maintaining current/next active state sets and processing epsilon transitions/classes/accept states.

State and persistence: compiled patterns are cached per SQL expression and freed via auxdata destructors; no database writes.

Dependencies/integration: SQLite extension APIs, limits, auxdata, and optional debug `regexp_bytecode()` in `SQLITE_DEBUG`.

Risks/test signals: `{m,n}` expansion, UTF-8 replacement behavior, ASCII-only case folding/word semantics, prefix optimization, and parser edge cases. Test supported syntax, malformed patterns, pattern-size limits, null inputs, REGEXP operator argument order, `regexpi()`, Unicode input, and debug bytecode.
