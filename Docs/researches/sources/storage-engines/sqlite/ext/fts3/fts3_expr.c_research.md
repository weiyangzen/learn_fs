# sources/storage-engines/sqlite/ext/fts3/fts3_expr.c

## Purpose

Implements the hand-written parser for FTS3/FTS4 `MATCH` query strings. It converts user query text into `Fts3Expr` trees containing phrase nodes and boolean/proximity operators, with legacy syntax support and optional parenthesized syntax controlled by `sqlite3_fts3_enable_parentheses` or `SQLITE_ENABLE_FTS3_PARENTHESIS`.

## Important APIs, types, and functions

`ParseContext` carries the tokenizer, language id, column names, default column, FTS4 feature flag, error context, and parenthesis nesting state. Public entry points are `sqlite3Fts3ExprParse()`, `sqlite3Fts3ExprFree()`, `sqlite3Fts3OpenTokenizer()`, and `sqlite3Fts3MallocZero()`. Parser internals include `getNextToken()`, `getNextString()`, `getNextNode()`, `fts3ExprParse()`, `insertBinaryOperator()`, `fts3ExprBalance()`, and `fts3ExprCheckDepth()`. Under `SQLITE_TEST`, `sqlite3Fts3ExprInitTestInterface()` registers `fts3_exprtest` and `fts3_exprtest_rebalance`.

## Control flow

Parsing repeatedly asks `getNextNode()` for the next keyword, parenthesized subexpression, quoted phrase, or tokenizer-normalized token. `getNextNode()` recognizes `OR`, `AND`, `NOT`, and `NEAR[/N]`, handles column prefixes for unquoted terms, and recurses into `fts3ExprParse()` for parentheses. `fts3ExprParse()` inserts implicit `AND` nodes, handles legacy unary `-` as a deferred `NOT` branch, rejects illegal NEAR operands, and uses precedence-aware insertion to build a tree. The public wrapper then balances `AND`/`OR` trees and enforces `SQLITE_FTS3_MAX_EXPR_DEPTH`.

## State and persistence

The file creates transient heap-owned expression trees. Phrase allocations combine `Fts3Expr`, `Fts3Phrase`, phrase-token metadata, and token text in one block where possible. No database state is persisted, but parsed expressions are later attached to `Fts3Cursor` evaluation state and freed by non-recursive traversal to avoid stack overflow.

## Dependencies and integration points

Depends on `fts3Int.h`, tokenizer modules through `sqlite3_tokenizer_module`, FTS phrase/evaluation cleanup via `sqlite3Fts3EvalPhraseCleanup()`, varint parsing for NEAR distances via `sqlite3Fts3ReadInt()`, and error formatting via `sqlite3Fts3ErrMsg()`. Integration is central to `MATCH` execution, snippet/matchinfo phrase iteration, and FTS4 first-token `^` syntax.

## Risks and test signals

Risks include tokenizer callbacks consuming quote/parenthesis delimiters, expression-depth denial of service, OOM during two-pass phrase allocation, mismatched parenthesis state, precedence differences between legacy and parenthesized modes, and non-phrase operands around `NEAR`. Test signals are `fts3_exprtest`, rebalance tests, malformed MATCH error strings, max-depth failures, prefix and column-qualified token cases, legacy `-term` behavior, and parenthesized `AND`/`NOT` syntax coverage.
