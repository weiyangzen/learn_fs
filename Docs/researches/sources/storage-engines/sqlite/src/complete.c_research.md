# sources/storage-engines/sqlite/src/complete.c

## Purpose

`complete.c` implements `sqlite3_complete()`, `sqlite3_complete16()`, and the internal diagnostic `sqlite3_incomplete()`. It tokenizes enough SQL to decide whether a string ends at a complete statement boundary, including comments, quoted strings/identifiers, parentheses, and the special `CREATE TRIGGER ...; END;` termination rule.

## Important APIs, Types, and Functions

- `sqlite3_incomplete(const char*)` scans UTF-8 SQL and returns 0 for complete input or a packed nonzero diagnostic value for missing terminators.
- `sqlite3_complete()` returns the public boolean completion result.
- `sqlite3_complete16()` converts UTF-16 input to UTF-8 using a transient `sqlite3_value` and then delegates to `sqlite3_incomplete()`.
- Token constants include `tkSEMI`, `tkWS`, `tkOTHER`, and, when triggers are enabled, keyword tokens for `EXPLAIN`, `CREATE`, `TEMP`, `TRIGGER`, and `END`.
- `IdChar` is imported from tokenizer behavior for ASCII or EBCDIC builds.

## Control Flow and Behavior

The scanner is a hand-written state machine. Without triggers, it only needs states for invalid/start/normal and detects a final semicolon outside quotes/comments. With triggers enabled, the eight-state transition table distinguishes beginning-of-statement `EXPLAIN`, `CREATE`, optional `TEMP`/`TEMPORARY`, `TRIGGER`, first semicolon, `END`, and final semicolon. Whitespace never changes state.

The loop skips or validates lexical structures: C comments must close with `*/`, SQL comments run to newline, bracket identifiers must close with `]`, and quote/backtick strings must close with the same delimiter. Parentheses adjust `nParen` even though the public result still treats a semicolon-terminated statement as complete; the richer `sqlite3_incomplete()` return packs unmatched parenthesis count in upper bits. On finish, `statemap[state]` reports whether a semicolon or trigger tail is missing, and `pending` reports an unterminated quote/comment marker.

## State and Persistence

All state is local to the scan: current state, token, pending delimiter, and parenthesis count. `sqlite3_complete16()` may initialize SQLite unless autoinit is omitted and allocates a temporary value for transcoding. The file does not mutate database state or parse schema objects.

## Dependencies and Integration Points

The public API is used by shells and client libraries to decide whether more SQL text is needed. It depends on tokenizer character-class tables, case-insensitive comparison helpers, UTF-16 value conversion, and optional `sqlite3_initialize()`. Compile-time options change behavior for triggers, explain, UTF-16, API armor, ASCII, and EBCDIC.

## Risks and Edge Cases

The scanner is intentionally not a full SQL parser. It handles quote closure by searching the next matching delimiter and does not process doubled SQL quotes as escapes during this completion pass, so behavior must match SQLite's historical API contract and tests. Trigger completion is sensitive to recognizing keywords only at statement start. A trailing SQL comment without newline is considered pending only if the state is not already `START`. NULL input returns `SQLITE_MISUSE_BKPT` only under API armor; otherwise callers must avoid NULL.

## Test Signals

Tests should include empty and whitespace-only strings, simple semicolon completion, unterminated C/SQL comments, single/double/backtick/bracket quoted text, trigger bodies ending with `;END;`, `EXPLAIN CREATE TEMP TRIGGER`, trigger-disabled builds, unmatched parentheses diagnostics through `sqlite3_incomplete()`, UTF-16 inputs, EBCDIC character classes where supported, and NULL input under API armor.
