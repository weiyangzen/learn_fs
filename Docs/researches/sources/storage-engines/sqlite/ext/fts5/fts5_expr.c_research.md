# sources/storage-engines/sqlite/ext/fts5/fts5_expr.c

## Purpose
`fts5_expr.c` parses MATCH expressions into an FTS5 expression tree, initializes index iterators for terms and prefixes, evaluates boolean/phrase/NEAR/column-constrained matches, exposes phrase position lists to auxiliary APIs, supports trigram LIKE/GLOB pattern acceleration, and registers debug/test scalar functions for expression rendering and Unicode helpers.

## Important APIs, types, and functions
- `Fts5Expr` owns the root node, config pointer, index pointer, rowid direction, and phrase array.
- `Fts5ExprNode` represents AND, OR, NOT, STRING/NEAR, TERM, or empty-match nodes. Each node stores EOF/nomatch state, current rowid, tree height, child pointers, and an `xNext` method.
- `Fts5ExprTerm` stores term bytes, query length versus full tokendata length, prefix/first-token flags, an index iterator, and synonym chain.
- `Fts5ExprPhrase` stores ordered terms and the current phrase poslist. `Fts5ExprNearset` groups phrases under a NEAR distance and optional column set.
- `sqlite3Fts5ExprNew()` tokenizes expression syntax, drives the Lemon parser, applies implicit LHS column filters, and returns an expression.
- `sqlite3Fts5ExprPattern()` converts trigram LIKE/GLOB patterns into a MATCH expression matching a superset of rows.
- `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, and `sqlite3Fts5ExprRowid()` provide the row iteration API.
- Parser callbacks such as `sqlite3Fts5ParseTerm()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseNode()`, `sqlite3Fts5ParseImplicitAnd()`, and colset functions are called by generated parser code.
- Auxiliary-facing APIs include phrase count/size, poslist access, collist access, cloned phrase expressions, query token access, inst-token lookup, poslist population for low-detail tables, and token-map clearing.

## Control flow
The lexer `fts5ExprGetToken()` recognizes operators, braces, parentheses, quoted strings, barewords, prefix markers, and special keywords. `sqlite3Fts5ExprNew()` feeds tokens into the generated parser, then optionally wraps the whole expression in a one-column colset if the MATCH left-hand side is a user column. Node construction assigns specialized `xNext` methods and flattens compatible AND/OR children, while enforcing maximum expression depth.

Iteration starts with `sqlite3Fts5ExprFirst()`. For each string/term node, `fts5ExprNearInitAll()` opens an `Fts5IndexIter` for every term and synonym via `sqlite3Fts5IndexQuery()`, using prefix and descending flags plus the node colset. TERM nodes can point directly at index-provided poslists. STRING nodes synchronize multiple term iterators to the same rowid, synthesize phrase poslists, merge synonym poslists, apply `^` first-token constraints, and trim NEAR matches.

Boolean nodes combine child iterators. OR selects the earliest rowid in iteration order, preferring real matches over `bNomatch` at equal rowid. AND advances lagging children until all rowids align; if any aligned child is only a structural/non-poslist match, the parent may become `bNomatch` and skip at the root. NOT advances the exclusion side to the include side and suppresses rows where the right child also matches. The public `First` and `Next` loops skip root `bNomatch` entries and enforce caller-provided rowid bounds.

Parsing terms uses `sqlite3Fts5Tokenize()` with `FTS5_TOKENIZE_QUERY` and optional prefix mode. Colocated tokenizer tokens become synonym chains. For `tokendata`, the query key length stops at the embedded NUL but the full term bytes remain available for token-return APIs. Detail modes restrict phrase/NEAR/column queries: without full detail, phrase and NEAR queries are rejected except for transformed trigram pattern cases.

## State and persistence behavior
This file is mostly transient query state. It owns expression nodes, phrases, synonym objects, poslist buffers, and index iterators. It reads persistent index data through `Fts5IndexIter` but does not write table state except for `sqlite3Fts5IndexIterWriteTokendata()` calls while populating token mappings for `xInstToken()` on prefix/tokendata queries. Debug/test scalar functions allocate temporary configs and expressions to print parse trees.

## Dependencies and integration points
The file depends on generated `fts5parse.h` and Lemon parser functions, `fts5_config.c` tokenizer and config APIs, `fts5_buffer.c` poslist/buffer helpers, `fts5_index.c` query/iterator/token-data APIs, Unicode helpers for debug/test functions, and SQLite allocation/UDF APIs. It is central to `fts5_main.c` query execution and to auxiliary functions that use phrase counts, position lists, instance tokens, and cloned phrase queries.

## Risks and edge cases
- Iterator direction is abstracted by `fts5RowidCmp()`; any direct numeric rowid comparison in this file must respect `bDesc` or DESC queries regress.
- Phrase and NEAR matching rewrite poslists in place. The logic relies on output positions being a subset of input positions.
- Synonym handling merges multiple poslists and skips duplicate positions; OOM during dynamic reader allocation must free temporary buffers correctly.
- `bNomatch` is subtle. Low-detail, column-filtered, AND, OR, and NOT paths can produce rows that satisfy term/doclist constraints but not final position semantics.
- Expression depth is capped by `SQLITE_FTS5_MAX_EXPR_DEPTH`; parser flattening reduces depth for repeated AND/OR but NOT remains binary.
- `sqlite3Fts5ExprPattern()` builds a superset expression for trigram patterns. Correct final LIKE/GLOB filtering must happen outside this file.
- Column filters are disallowed for `detail=none`; phrase/NEAR restrictions for `detail!=full` are enforced during node construction and pattern conversion.
- `sqlite3Fts5ExprClearTokens()` assumes iterators exist for every term; callers must only invoke it after iterator initialization.

## Test signals
Tests should cover tokenization of quoted strings and barewords, syntax errors, implicit AND, explicit AND/OR/NOT precedence, expression-depth limits, column sets and inverted colsets, missing columns, LHS column filters, prefix terms, synonyms/colocated tokens, `^` first-token phrases, phrase and NEAR poslist trimming, ascending and descending rowid iteration, rowid bounds, detail=none/detail=columns restrictions and poslist population, trigram LIKE/GLOB superset generation, tokendata embedded-NUL behavior, xQueryToken/xInstToken APIs, and debug expression printers under test builds.
