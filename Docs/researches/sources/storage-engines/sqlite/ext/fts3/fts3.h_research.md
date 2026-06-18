# sources/storage-engines/sqlite/ext/fts3/fts3.h

## Purpose
`fts3.h` is the small public header for code that links against SQLite's FTS3 extension. It exposes the single initialization function needed to register the FTS3/FTS4 extension with a database connection.

## Important APIs, Types, And Functions
The only declared API is `int sqlite3Fts3Init(sqlite3 *db);`. Callers pass an open SQLite connection, and the implementation in `fts3.c` registers the FTS3/FTS4 modules, tokenizers, auxiliary modules, and overloaded functions on that connection.

The header includes `sqlite3.h` so the `sqlite3` connection type and SQLite result codes are visible. It wraps the declaration in `extern "C"` when included from C++ so C++ clients can link against the C implementation.

## Control Flow
There is no runtime control flow in this header. It is included by extension or core build units that need the declaration. Loadable-extension builds ultimately call `sqlite3_fts3_init()` in `fts3.c`, which initializes the SQLite extension API table and delegates to `sqlite3Fts3Init()`.

## State And Persistence Behavior
The header owns no state and writes no data. The function it declares mutates the supplied SQLite connection by registering modules and functions. Persistent FTS shadow tables are created later only when users create FTS virtual tables.

## Dependencies
The direct dependency is `sqlite3.h`. The declared function depends at link time on the FTS3 implementation and its sibling tokenizer, expression, snippet, auxiliary, and write modules.

## Integration Points
SQLite core builds may call `sqlite3Fts3Init()` directly during extension initialization. External embedders or loadable extension code can include this header to register FTS3 support on a specific connection without relying on private internal headers.

## Risks And Edge Cases
The header intentionally exposes only initialization. It does not expose tokenizer registration helpers, FTS table structures, or evaluator internals. Consumers that need deeper behavior must use SQLite SQL APIs or internal headers, not this public header.

The main integration risk is build mismatch: including this header without linking the FTS3 implementation produces unresolved symbols, and calling the initializer in a build where FTS3 is omitted will not be available.

## Test Signals
Compilation tests should verify that C and C++ translation units can include the header. Runtime smoke tests should call `sqlite3Fts3Init()` on a database connection and then successfully execute `CREATE VIRTUAL TABLE t USING fts3(...)` or `fts4(...)`.
