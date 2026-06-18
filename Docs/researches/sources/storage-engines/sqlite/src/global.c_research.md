# sources/storage-engines/sqlite/src/global.c

## Purpose

`global.c` defines process-global SQLite constants and mutable configuration state. It provides character classification/case tables, comparison opcode truth tables, default compile-time configuration values, the singleton `sqlite3Config`, the global built-in function hash, diagnostic counters, the default pending-byte location, tracing flags, opcode properties, the default collation name, and standard type-name metadata.

## Important APIs, Types, And Data

Key exported objects are `sqlite3UpperToLower`, `sqlite3aLTb`, `sqlite3aEQb`, `sqlite3aGTb`, `sqlite3CtypeMap`, `sqlite3Config`, `sqlite3BuiltinFunctions`, optional `sqlite3CoverageCounter`, optional `sqlite3NProfileCnt`, `sqlite3PendingByte`, `sqlite3TreeTrace`, `sqlite3WhereTrace`, `sqlite3OpcodeProperty`, `sqlite3StrBINARY`, `sqlite3StdTypeLen`, `sqlite3StdTypeAffinity`, and `sqlite3StdType`.

`sqlite3UpperToLower` maps bytes for ASCII or EBCDIC lowercasing. It intentionally appends 18 boolean entries used by comparison opcode truth tables to avoid out-of-bounds indexing. `sqlite3CtypeMap` is SQLite's compact replacement for libc character classifiers. `sqlite3Config` is a `SQLITE_WSD struct Sqlite3Config` initialized from many compile-time defaults such as URI behavior, lookaside size, mmap limits, sorter settings, memory methods, mutex methods, page-cache methods, deserialize limits, localtime fault hooks, and debug tuning fields.

## Control Flow

The file mostly has static initialization, not executable control flow. SQLite startup and configuration APIs read and mutate `sqlite3Config` during initialization. VDBE, tokenizer, parser, expression comparison, and planner code read the lookup tables and globals directly. `opcodes.h` supplies `OPFLG_INITIALIZER` for `sqlite3OpcodeProperty`.

## State And Persistence Behavior

State is process-global. `sqlite3Config` is mutable during global initialization and through `sqlite3_config()` paths, then much of it becomes effectively fixed while SQLite is initialized. `sqlite3PendingByte` can be changed by test control when writable static data is available, but changing it away from `0x40000000` makes database file locking layout incompatible and is for testing only. Trace flags and coverage counters are diagnostic process state. None of these globals are stored in a database file, although settings such as pending-byte location and mmap limits influence file access behavior.

## Dependencies And Integration Points

This file depends on `sqliteInt.h` and generated `opcodes.h`. It is consumed broadly by tokenizer and identifier logic, SQL comparison opcodes, memory/mutex/page-cache initialization, VDBE opcode metadata, built-in function registration in `func.c`, type-affinity code, and test-control/debug facilities. Compile-time macros heavily shape the initialized values: `SQLITE_ASCII`, `SQLITE_EBCDIC`, `SQLITE_USE_URI`, `SQLITE_ALLOW_COVERING_INDEX_SCAN`, `SQLITE_SORTER_PMASZ`, `SQLITE_STMTJRNL_SPILL`, `SQLITE_DEFAULT_LOOKASIDE`, `SQLITE_MEMDB_DEFAULT_MAXSIZE`, `SQLITE_ENABLE_SQLLOG`, `SQLITE_VDBE_COVERAGE`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_ALLOW_ROWID_IN_VIEW`, `SQLITE_DEBUG`, `VDBE_PROFILE`, and `SQLITE_OMIT_WSD`.

## Risks

The highest risks are ABI/layout drift in `Sqlite3Config` initialization, table contents that must match tokenizer/collation/opcode assumptions, and compile-time option combinations that change array contents or struct fields. The appended comparison truth-table trick relies on comparison opcodes being consecutive and ordered as expected. Character classification is deliberately ASCII/EBCDIC-centric and not Unicode case mapping. `sqlite3PendingByte` must not be changed in production. Since these are globals, thread-safety depends on SQLite's initialization and mutex protocol.

## Test Signals

Signals include startup/configuration tests, tokenizer and identifier classification tests, ASCII and EBCDIC build coverage where supported, comparison opcode truth-table assertions, type-affinity tests for standard type names, opcode-property generation checks, `sqlite3_config()` option tests, test-control coverage for pending-byte relocation, trace flag tests, and UBSAN/ASAN runs validating no out-of-bounds table access.
