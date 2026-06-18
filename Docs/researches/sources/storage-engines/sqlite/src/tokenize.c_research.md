# sources/storage-engines/sqlite/src/tokenize.c

## Purpose

`tokenize.c` implements SQLite's SQL tokenizer, parser driver, identifier-character helper, contextual handling for window-function keywords, and optional SQL normalization. It converts SQL text into Lemon parser tokens, manages parser lifecycle, records parse errors/tails, and normalizes SQL text for statement comparison when `SQLITE_ENABLE_NORMALIZE` is enabled.

## Important APIs, Types, And Functions

- `aiClass[]` maps input bytes to compact character classes used by `sqlite3GetToken()`.
- `charMap()` and generated `keywordhash.h` provide keyword lookup through `keywordCode()`.
- `IdChar()` and `sqlite3IsIdChar()` define legal identifier continuation characters for ASCII and EBCDIC builds.
- `getToken()`, `analyzeWindowKeyword()`, `analyzeOverKeyword()`, and `analyzeFilterKeyword()` resolve contextual `WINDOW`, `OVER`, and `FILTER` ambiguity.
- `sqlite3GetToken()` returns the byte length and token type for the next token.
- `sqlite3RunParser()` drives tokenization, Lemon parser allocation/finalization, interrupt checks, SQL length enforcement, error logging, cleanup of partially built parse objects, and tail tracking.
- `addSpaceSeparator()` and `sqlite3Normalize()` optionally build normalized SQL with literals replaced by `?`, identifiers lowercased, keywords uppercased, and IN-list RHS compressed.

## Control Flow

`sqlite3GetToken()` switches on `aiClass[*z]` for speed. It recognizes whitespace, comments, punctuation, operators, string and quoted identifiers, bracket identifiers, numeric and floating literals, hex integer and blob literals, variables, identifiers/keywords, UTF-8 BOMs, illegal characters, and NUL input. Keyword candidates call generated `keywordCode()` unless an identifier-only continuation is found. Numeric tokens containing configured digit separators become `TK_QNUMBER` so the parser driver can reject them as unrecognized.

`sqlite3RunParser()` allocates or stack-initializes the Lemon parser, installs the current `Parse` in `db->pParse`, clears interruption state when no VDBEs are active, then loops over tokens. It enforces `SQLITE_LIMIT_SQL_LENGTH`, skips spaces and allowed comments, synthesizes `TK_SEMI` and end token at input end, rewrites contextual window tokens when necessary, reports unrecognized tokens, and calls `sqlite3Parser()` with `pParse->sLastToken`. After parsing, it records parser stack highwater when enabled, frees the parser, maps malloc failure to `SQLITE_NOMEM_BKPT`, logs parse errors unless disabled, sets `pParse->zTail`, and frees parse-side structures such as vtab locks, abandoned new tables/triggers, and variable lists.

`sqlite3Normalize()` retokenizes original SQL. It removes comments and whitespace, replaces literals and bind variables with `?`, preserves `IS NULL` and `IS NOT NULL`, dequotes and lowercases identifiers, uppercases keywords/operators, compresses parenthesized RHS values of `IN` to `(?,?,?)`, and appends a semicolon if missing.

## State And Persistence Behavior

Tokenizer tables are static read-only state. Parser execution mutates the supplied `Parse` object, `db->pParse`, `db->u1.isInterrupted`, error strings, parser highwater status, and parse-owned allocations. It does not directly mutate database storage; parser actions called by Lemon grammar may build schema objects or VDBE programs that later change persistent state.

Normalization returns a newly allocated database-owned string from `sqlite3_str_finish()` and does not alter the original SQL. `pParse->zTail` points into the original SQL at the parse stopping point.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, generated `keywordhash.h`, generated Lemon parser APIs (`sqlite3Parser*`), SQLite character maps, limits, logging, memory allocation, VDBE statement metadata, schema object cleanup, virtual table parse locks, and optional normalization APIs. It is on the prepare path for every SQL statement.

## Risks And Edge Cases

- Token boundaries are security- and compatibility-sensitive; small changes affect all SQL parsing.
- Contextual `WINDOW`, `OVER`, and `FILTER` handling works around grammar fallback ambiguity and must remain synchronized with grammar rules.
- Quoted strings and identifiers have different illegal-token behavior on unterminated input; parser error offsets depend on returned lengths.
- Numeric digit separators intentionally become invalid `TK_QNUMBER` in the parser path unless accepted elsewhere; normalization must mirror token behavior.
- Comments are ignored only during schema initialization or when comments are enabled by DB config; otherwise comments can trigger unrecognized-token behavior.
- `sqlite3RunParser()` cleans partially built tables/triggers only outside special parse modes; mistakes can leak objects or double-free rename/vtab-owned objects.
- EBCDIC and ASCII paths share behavior through different tables; both need coverage when portability matters.

## Test Signals

Tests should cover every token class, comments, BOMs, quoted identifiers and strings, blob and hex literals, numeric separators, variables including Tcl-style names, illegal characters, SQL length limits, interrupts, parser tail handling, contextual window keywords, comment DB config, malloc failure cleanup, parser tracing/highwater, normalization of literals/identifiers/IN lists/double-quoted strings, and EBCDIC-specific identifier behavior where supported.
