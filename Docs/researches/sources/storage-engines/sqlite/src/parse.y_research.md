# sources/storage-engines/sqlite/src/parse.y

## Purpose

`parse.y` is SQLite's Lemon grammar for SQL parsing. Lemon translates it into C code for `sqlite3Parser`, and the grammar actions directly build SQLite AST and schema/DML objects using the `Parse *pParse` context. This file is not a passive syntax declaration; reductions call functions such as `sqlite3StartTable()`, `sqlite3SelectNew()`, `sqlite3Insert()`, `sqlite3Update()`, `sqlite3DeleteFrom()`, `sqlite3CreateIndex()`, `sqlite3BeginTrigger()`, `sqlite3WindowAlloc()`, and many expression constructors.

The grammar covers transactions, savepoints, table/view/index/trigger/virtual-table DDL, SELECT including compound SELECT and VALUES, INSERT/UPSERT/RETURNING, UPDATE/DELETE with optional limited forms, expressions, functions, subqueries, CTEs, window functions, PRAGMA, VACUUM, ATTACH/DETACH, REINDEX, ANALYZE, and ALTER TABLE extensions.

## Important APIs, Types, and Grammar Constructs

Parser setup uses `%token_prefix TK_`, `%token_type {Token}`, `%default_type {Token}`, `%extra_context {Parse *pParse}`, `%syntax_error`, `%stack_overflow`, and `%name sqlite3Parser`. Parser stack memory is controlled by `parserStackRealloc()`, `parserStackFree()`, and `parserStackSizeLimit()`, the latter using `SQLITE_LIMIT_PARSER_DEPTH`.

Embedded helper types include `struct TrigEvent` and `struct FrameBound`. Helper functions include `parserSyntaxError()`, `disableLookaside()`, `updateDeleteLimitError()` for capable parsers without enabled limited UPDATE/DELETE, `parserDoubleLinkSelect()`, `attachWithToSelect()`, `tokenExpr()`, `sqlite3ExprAddOrderedsetFunction()`, `sqlite3PExprIsNull()`, `sqlite3PExprIs()`, and `parserAddExprIdListTerm()`.

Key nonterminals carry typed semantic values: `select`, `oneselect`, `expr`, `term`, `exprlist`, `sortlist`, `seltablist`, `fullname`, `xfullname`, `setlist`, `upsert`, `idlist`, `eidlist`, `wqlist`, `window`, `frame_bound`, and `trigger_cmd`. `%destructor` rules free AST fragments if parse errors or stack unwinding leave them unused.

Token declarations and precedence are deliberately ordered. Operator tokens are clustered so code generator assumptions in expression evaluation remain valid. `TK_SPACE`, `TK_COMMENT`, and `TK_ILLEGAL` are declared last for tokenizer expectations. A compile-time check rejects grammars where synthesized tokens exceed the 255-token boundary through `TK_SPAN`.

## Control Flow

Input reduces as `input ::= cmdlist`, with each statement reducing through `cmdx ::= cmd` and then `sqlite3FinishCoding(pParse)`. Transaction commands call transaction helpers directly. DDL reductions disable lookaside for schema objects that may outlive one connection and then call schema builders. SELECT reductions build `Select` chains, link compound SELECT nodes with `parserDoubleLinkSelect()`, enforce compound SELECT limits, and attach `WITH` objects when present.

DML reductions build source lists, expression lists, WHERE and RETURNING clauses, then dispatch to the corresponding code generator. UPDATE with a FROM clause normalizes multi-source FROM into a nested SELECT source before appending it to the target source list. INSERT handles `DEFAULT VALUES`, SELECT input, UPSERT chains, and RETURNING.

Expression parsing builds `Expr` nodes for literals, identifiers, dotted names, variables, function calls, vectors, unary/binary operators, LIKE/MATCH infix functions, BETWEEN, IN, subqueries, EXISTS, CASE, CAST, COLLATE, ordered-set aggregate syntax, filters, and window attachments. Several reductions perform early normalization, such as `expr IN ()` to constants when safe, single-constant `IN` to equality, and `IS NULL` optimizations.

Trigger grammar captures source spans with `scanpt` so trigger steps can retain original SQL text. Virtual-table argument grammar uses a broad `ANY` token stream and explicit extension calls to preserve module arguments. Window grammar is placed near the end so `WINDOW`, `OVER`, and `FILTER` get token values above ordinary tokenizer outputs.

## State and Persistence Behavior

The parser mutates `Parse` state throughout: error counts, `explain`, `disableLookaside`, create-state union `u1.cr`, `isCreate` debug state, rename token maps, `hasCompound`, `bHasWith`, trigger construction state, returning clauses, and schema initialization compatibility paths. It allocates AST objects from the database connection, and destructors define ownership transfer on successful reductions.

Although parsing itself does not persist database pages, many reductions create persistent schema objects or SQL text stored in `sqlite_schema`. Compatibility behavior is visible in `eidlist`: older schemas with ignored COLLATE or ASC/DESC decorations in identifier lists are still accepted while `db->init.busy` is true. DDL actions use `disableLookaside()` because schema objects can be shared across connections.

## Dependencies and Integration Points

`parse.y` includes `sqliteInt.h` and is tightly coupled to tokenizer token names, AST structures (`Expr`, `ExprList`, `Select`, `SrcList`, `IdList`, `With`, `Cte`, `Window`, `TriggerStep`), schema builders, expression helpers, pragma/vacuum/attach/alter/vtab modules, and the VDBE code-generation pipeline. Lemon-specific directives are part of the build process, so changes require regenerating parser C output through the established SQLite build tooling.

## Risks and Edge Cases

Parser conflicts and token ordering are high risk. The grammar documents an UPSERT ambiguity where `ON` after a SELECT JOIN is resolved as a JOIN constraint unless a WHERE clause disambiguates the UPSERT. New tokens before the final boundary can break assumptions about token values. Error handling must delete partially built ASTs exactly once; incorrect `%destructor` ownership causes leaks or double frees. Feature macros such as `SQLITE_OMIT_*`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_ORDERED_SET_AGGREGATES`, and `SQLITE_UDL_CAPABLE_PARSER` create multiple grammars that all need coverage.

## Test Signals

Tests should cover full SQL syntax acceptance and rejection, parser stack depth limits, OOM/fault injection around parser stack reallocation and AST creation, rename-token mapping, schema-init compatibility parsing, all feature macro combinations used by builds, UPSERT ambiguity cases, RETURNING with INSERT/UPDATE/DELETE, UPDATE FROM, trigger statement restrictions, virtual-table argument preservation, CTE materialization hints, ordered-set aggregate errors, and window frame/filter/over combinations.
