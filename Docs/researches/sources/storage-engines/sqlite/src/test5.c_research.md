<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test5.c -->
# sources/storage-engines/sqlite/src/test5.c

## Purpose
`test5.c` supports UTF and value conversion tests. It gives Tcl scripts byte-level access to UTF encodings, measures `sqlite3_value_text()` overhead on a constructed `Mem`, and calls the internal UTF self-test.

## Important APIs, Types, and Functions
Commands registered by `Sqlitetest5_Init()` are `binarize`, `test_value_overhead`, `test_translate`, and `translate_selftest`. The implementation uses `Mem` from `vdbeInt.h`, `sqlite3_value`, `sqlite3ValueNew()`, `sqlite3ValueSetStr()`, `sqlite3ValueText()`, `sqlite3ValueBytes()`, `sqlite3ValueFree()`, and internal `sqlite3UtfSelfTest()`. `name_to_enc()` maps Tcl names `UTF8`, `UTF16LE`, `UTF16BE`, and `UTF16` to SQLite encoding constants.

## Control Flow
`binarize()` converts a Tcl UTF-8 string to a Tcl byte-array including its terminating zero byte. `test_value_overhead()` creates a static UTF-8 `Mem` containing `hello world` and loops `repeat_count` times, optionally invoking `sqlite3_value_text()`. `test_translate()` constructs a `sqlite3_value` from either Tcl string text or byte-array data in the requested source encoding, converts it to the target encoding, returns the converted bytes plus terminator, and frees the value. The optional fifth argument forces transient allocation with `sqlite3_free` as destructor.

## State and Persistence Behavior
The file has no durable state. It creates short-lived SQLite value objects and returns Tcl byte arrays. The transient path tests destructor ownership by allocating a separate SQLite buffer. `translate_selftest` runs internal asserts when UTF16 support is compiled in.

## Dependencies and Integration Points
This harness depends on SQLite VDBE memory internals, encoding constants, Tcl object byte-array APIs, and compile-time `SQLITE_OMIT_UTF16`. It directly exercises APIs below the public SQL interface, making it useful for encoding regressions that normal SQL tests may hide.

## Risks
`test_value_overhead()` manually initializes only the `Mem` fields it needs; changes to `Mem` invariants can make this test stale. `test_translate()` passes `-1` byte counts for UTF16 byte arrays, which relies on SQLite string routines finding terminators. The optional transient branch allocates exactly `len` bytes for non-UTF8 input, so tests must supply properly terminated encoded byte arrays when required.

## Test Signals
Expected signals are byte-for-byte translated output including terminators, invalid encoding names returning Tcl errors, performance/no-op behavior of repeated value-text calls, and assertion failures from `sqlite3UtfSelfTest()` in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test5.c -->
