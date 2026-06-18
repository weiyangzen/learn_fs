# sources/storage-engines/sqlite/ext/misc/normalize.c

Purpose: implements `sqlite3_normalize()`, a standalone SQL normalizer that replaces literals, removes comments/extra whitespace, lowercases ASCII, and canonicalizes simple `IN` lists.

Important APIs/types/functions: copied tokenizer tables `aiClass`, `sqlite3UpperToLower`, and `sqlite3CtypeMap`; `sqlite3GetToken()`; `sqlite3_normalize()`; optional CLI helpers `normalizeFile()` and `main()` under `SQLITE_NORMALIZE_CLI`.

Control flow: tokenizes input, drops whitespace/comments, replaces literals and most `NULL` constants with `?`, lowercases names/punctuation text, inserts required spaces, appends a semicolon, then rewrites non-subquery `in(...)` lists to `in(?,?,?)`.

State and persistence: returns caller-owned `sqlite3_malloc64()` memory. CLI reads files and prints normalized statements only.

Dependencies/integration: public SQLite allocation/completion APIs. Tokenizer logic intentionally tracks a snapshot of SQLite core tokenization.

Risks/test signals: tokenizer drift, ASCII-only folding, coarse string-search `IN` rewrite, malformed SQL returning null, and missed literal forms. Test quoted identifiers, comments, strings/blobs/numbers/variables, `IS NULL`, nested and subquery `IN`, non-ASCII identifiers, invalid tokens, and CLI statement splitting.
