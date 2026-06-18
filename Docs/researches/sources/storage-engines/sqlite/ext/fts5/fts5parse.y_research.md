# sources/storage-engines/sqlite/ext/fts5/fts5parse.y

## Purpose
`fts5parse.y` is the Lemon grammar for FTS5 `MATCH` expressions. It turns expression tokens into FTS5 expression nodes, nearsets, phrases, column filters, implicit ANDs, prefixes, and NEAR groups.

## Important APIs, Types, And Functions
The generated parser is named `sqlite3Fts5Parser` and receives `Fts5Parse *pParse`. Semantic values include `Fts5Token`, `Fts5ExprNode *`, `Fts5ExprNearset *`, `Fts5ExprPhrase *`, and `Fts5Colset *`. Grammar actions call helpers such as `sqlite3Fts5ParseFinished()`, `sqlite3Fts5ParseNode()`, `sqlite3Fts5ParseImplicitAnd()`, `sqlite3Fts5ParseColset()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseSetDistance()`, and `sqlite3Fts5ParseTerm()`.

## Control Flow
The grammar starts at `input ::= expr`. Boolean operators create AND/OR/NOT nodes with declared precedence. Adjacent cnearsets become implicit AND nodes. Column filters parse as strings, braced lists, or inverted forms and apply to expressions or nearsets. Nearsets parse phrases, caret-anchored phrases, or `NEAR(...)` with optional distance. Phrases parse `+`-joined string terms and optional trailing `*` prefix markers. Syntax and stack errors are reported through `Fts5Parse`, and destructors free partial AST objects.

## State And Persistence
Generated parser stack state is transient. Successful parsing produces an expression tree consumed by query execution; no database state is directly changed.

## Dependencies And Integration Points
The grammar includes `fts5Int.h` and `fts5parse.h`, depends on Lemon generation, and defines user-visible FTS5 query syntax.

## Risks
Operator precedence and implicit AND behavior are user-visible. Destructor correctness affects parse-error memory safety. Column-filter inversion, nested filters, caret, NEAR, and prefix parsing must match FTS5 documentation. Error recovery is disabled, making first-error reporting important.

## Test Signals
Cover boolean precedence, implicit AND, parentheses, NOT, column filters, inverted filters, braced lists, caret, NEAR distance, phrase `+`, prefix `*`, syntax errors, and deeply nested expressions.
