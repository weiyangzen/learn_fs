# sources/storage-engines/rocksdb/options/options_settable_test.cc

Purpose: provides regression tests that detect newly added option fields that cannot be set through RocksDB's string/configuration parsing APIs.

Important APIs, types, and functions: helper routines `FillWithSpecialChar`, `NumUnsetBytes`, and `CompareBytes` operate on raw object storage while skipping excluded field ranges. Test cases include `BlockBasedTableOptionsAllFieldsSettable`, `TablePropertiesAllFieldsSettable`, `DBOptionsAllFieldsSettable`, and `ColumnFamilyOptionsAllFieldsSettable`. The test binary installs the stack trace handler, initializes GoogleTest, and optionally parses gflags.

Control flow: each test allocates raw memory for the target option struct, fills all non-excluded bytes with a sentinel, constructs or copies a default object to count padding bytes, then parses a comprehensive option string into a second sentinel-filled object. The assertion compares remaining sentinel bytes against the expected padding count; if a real field remains untouched, the count changes and the test fails. Some tests add explicit semantic checks for pointer/custom fields or nested structs that must be excluded from raw byte comparison.

State and persistence behavior: tests do not persist files, but they validate the in-memory parse targets that persisted option strings rely on. `DBOptionsAllFieldsSettable` also checks that `BuildDBOptions({}, {}, *options)` initializes all non-excluded fields. The CF test checks round-tripping from `ColumnFamilyOptions` through `MutableCFOptions` and back using byte comparison over mutable fields.

Dependencies and integration points: includes `cf_options.h`, `db_options.h`, `options_helper.h`, public convenience APIs, and RocksDB test harness. It exercises block-based table option parsing, `TableProperties::Parse`, `GetDBOptionsFromString`, `GetColumnFamilyOptionsFromString`, `BuildDBOptions`, `MutableCFOptions`, and `BuildColumnFamilyOptions`.

Risks: the file openly depends on compiler behavior around padding bytes and is disabled for clang, UBSAN, and some status-check configurations. Excluded offset ranges must stay sorted and accurate; wrong exclusions can hide missing parser coverage or produce false failures. Because tests use large hand-written option strings, schema updates require careful edits in multiple places.

Test signals: these are themselves the test signals for the options schema. Failing comments explain the required fix path: add the new option to the appropriate parser/config metadata and update the test string or excluded list for complex fields. The platform guards mean CI coverage may be incomplete on unsupported compiler/sanitizer combinations.
