# sources/storage-engines/sqlite/ext/rtree/rtree.h

## Purpose
`rtree.h` is the small internal/public bridge header for linking SQLite's R-Tree extension into a build. It declares the initializer that registers the R-Tree virtual table modules and helper functions on a database connection.

## Important APIs, Types, And Functions
The only declared function is `int sqlite3RtreeInit(sqlite3 *db);`. It takes an open SQLite connection and returns an SQLite result code. The implementation in `rtree.c` registers `rtree`, `rtree_i32`, `rtreenode()`, `rtreedepth()`, `rtreecheck()`, and optional geopoly support.

The header includes `sqlite3.h` for the `sqlite3` type. If `SQLITE_OMIT_VIRTUALTABLE` is set, it undefines `SQLITE_ENABLE_RTREE`, reflecting that R-Tree cannot be enabled without SQLite virtual tables.

## Control Flow
There is no runtime control flow in this header. Compile-time flow is limited to feature guards and C++ linkage wrapping. Consumers include the header and call `sqlite3RtreeInit()` during extension or core initialization.

## State And Persistence Behavior
The header owns no state and persists nothing. The declared function mutates only the supplied SQLite connection by registering modules and functions. Persistent shadow tables are created later by SQL `CREATE VIRTUAL TABLE` statements handled in `rtree.c`.

## Dependencies
The direct dependency is `sqlite3.h`. Link-time dependency is the R-Tree implementation object that defines `sqlite3RtreeInit()`. Builds omitting virtual tables must not expect R-Tree registration to be available.

## Integration Points
SQLite core initialization or extension bootstrap code can use this header to register R-Tree support. C++ consumers are supported through `extern "C"`.

## Risks And Edge Cases
The main risk is build configuration mismatch: including this header without compiling the implementation produces unresolved symbols, while defining `SQLITE_OMIT_VIRTUALTABLE` suppresses the feature macro. The header intentionally exposes no node, cursor, or callback internals; users needing callback APIs should include `sqlite3rtree.h`.

## Test Signals
Compilation tests should include this header from C and C++ translation units. Runtime smoke tests should call `sqlite3RtreeInit()` and then create/query a simple `rtree` and `rtree_i32` table.
