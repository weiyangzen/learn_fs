# sources/storage-engines/sqlite/ext/icu/sqliteicu.h

## Purpose
`sqliteicu.h` is the public header for applications that statically link the ICU extension. It declares the initializer used to register ICU functions with a connection.

## Important APIs, Types, And Functions
The single API is `int sqlite3IcuInit(sqlite3 *db);`. The header includes `sqlite3.h` and uses `extern "C"` for C++ compatibility.

## Control Flow
The header has no runtime control flow. Consumers include it and call `sqlite3IcuInit(db)`.

## State And Persistence
No state is owned here. The implementation registers per-connection SQL functions and collations.

## Dependencies And Integration Points
It depends on SQLite public headers and a linked `icu.c` object plus ICU libraries. It is the static-link counterpart to `sqlite3_icu_init()`.

## Risks
There is no include guard, though repeated identical declarations are normally harmless. Consumers must link the implementation and ICU libraries.

## Test Signals
Compile from C and C++, statically link the extension, call `sqlite3IcuInit()`, and verify ICU SQL functions and collations are available.
