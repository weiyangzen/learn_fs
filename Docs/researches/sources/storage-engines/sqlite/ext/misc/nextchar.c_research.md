# sources/storage-engines/sqlite/ext/misc/nextchar.c

Purpose: registers `next_char(prefix, table, column[, where[, coll]])`, an autocomplete helper returning distinct next UTF-8 characters after a prefix in a vocabulary column.

Important APIs/types/functions: `nextCharContext` holds the database, statement, prefix, result array, and error flags. `writeUtf8()`, `readUtf8()`, `nextCharAppend()`, `findNextChars()`, and `nextCharFunc()` implement the logic. `sqlite3_nextchar_init()` registers 3-, 4-, and 5-argument variants.

Control flow: builds dynamic SQL over caller-supplied table/column/where/collation, constrains values between prefix lower/upper bounds, orders by the vocabulary column, and repeatedly binds the previous character boundary to find the next distinct code point.

State and persistence: per-call prepared statement and result array only; no writes.

Dependencies/integration: SQLite dynamic SQL and indexes/collations on the target vocabulary for performance.

Risks/test signals: identifier/expression arguments are SQL text and unsafe if untrusted, UTF-8 handling is permissive, and missing indexes are slow. Test quoted identifiers, subqueries, where/collation options, multibyte characters, duplicate suppression, malformed SQL, empty prefixes, and allocation failures.
