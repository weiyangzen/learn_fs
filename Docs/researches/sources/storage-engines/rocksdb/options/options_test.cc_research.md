# Research: sources/storage-engines/rocksdb/options/options_test.cc

## Purpose
This file is the central unit-test suite for RocksDB option parsing, option serialization, persisted OPTIONS-file parsing, option sanity checking, and object-registry based configuration. It exercises both newer `ConfigOptions`/`Configurable` paths and older convenience APIs so compatibility is preserved while options continue to move to typed registration.

## Important APIs, Types, And Functions
The tests target public and internal option helpers including `GetColumnFamilyOptionsFromMap`, `GetDBOptionsFromMap`, `GetColumnFamilyOptionsFromString`, `GetDBOptionsFromString`, `GetOptionsFromString`, `GetStringFromDBOptions`, `GetStringFromColumnFamilyOptions`, `GetStringFromMutableDBOptions`, `GetMutableDBOptionsFromStrings`, `StringToMap`, `MapToString`, `PersistRocksDBOptions`, and `RocksDBOptionsParser::Parse`/`Verify*`.

Fixtures and helper types include `OptionsTest`, `OptionsOldApiTest`, `OptionsParserTest`, `OptionsSanityCheckTest`, `OptionTypeInfoTest`, and `ConfigOptionsTest`. Local test doubles cover unregistered table factories, custom environments, event listeners, table properties collectors, and mock file checksum factories. The file also directly exercises `OptionTypeInfo` for primitive, enum, struct, array, vector, static type-map, parse, serialize, compare, prepare, validate, and flag behavior.

## Control Flow
The first block validates map and string parsing into `ColumnFamilyOptions`, `DBOptions`, and merged `Options`, checking both successful assignment and failure preservation when bad values or unknown keys are provided. It covers scalar values, memory-size suffixes, enum strings, nested structs, colon-separated legacy encodings, pointer/object factories, caches, filter policies, compression options, blob options, temperatures, timestamps, and mutable-only filtering.

The middle of the file validates round trips. Randomized option objects are serialized to strings, parsed back, decomposed/recomposed through immutable and mutable option structures, and compared with `RocksDBOptionsParser::Verify*`. `StringToMap` and `MapToString` are stressed with nested braces, empty braced values, random malformed strings, escaping, and single-entry round trips so generated map values remain embeddable in `key=value;` contexts.

The parser-focused tests write temporary OPTIONS files through a special filesystem, then parse sections such as `[Version]`, `[DBOptions]`, and `[CFOptions "name"]`. They assert rejection of missing or duplicate required sections, invalid default-CF ordering, invalid versions, duplicate CF entries, and conditional unknown-option behavior based on persisted RocksDB version. Dump-and-parse tests persist multiple column families with unusual names and pointer-valued options, then verify parsed DB/CF options and per-option maps.

The sanity-check tests persist options and then vary prefix extractors, table factories, merge operators, compaction filters, compaction filter factories, file checksum factories, and `persist_user_defined_timestamps` under exact, loosely compatible, and disabled sanity levels. The parameterization runs with `ignore_unsupported_options` both true and false.

## State And Persistence Behavior
Most tests are pure in-memory configuration transformations. Parser tests create and delete temporary files such as `test-rocksdb-options.ini`, `test-persisted-options.ini`, and `OPTIONS` through the fixture filesystem, including persisted RocksDB OPTIONS metadata. No real DB data is written, but the test simulates durable options files that DB reopen flows rely on.

The object registry is mutated during tests to register comparators, environments, event listeners, and table-property collector factories. Several randomly initialized CF options allocate raw `compaction_filter` pointers, and the tests explicitly delete those pointers after verification. A custom filesystem read counter is used to assert readahead behavior while parsing large persisted option files.

## Dependencies And Integration Points
The suite integrates with RocksDB option implementation files (`options_helper`, `options_parser`, configurable wrappers), table factories and filter policies, caches, memtable factories, merge operators, object registry, file checksum factories, LevelDB option conversion, test randomizers, special environment/filesystem helpers, and the port stack-trace handler used by `main`.

It is a regression net for DB reopen safety because `RocksDBOptionsParser::VerifyRocksDBOptionsFromFile` determines whether current runtime options are compatible with persisted metadata. It also protects Java and other bindings indirectly because those layers commonly use the same string and map option APIs.

## Risks And Edge Cases
The test file is intentionally broad and can become brittle when option defaults or serialization names change. Failures often indicate either an intentional compatibility change requiring test updates or a real break in persisted OPTIONS compatibility. Pointer-valued option comparisons are subtle: some unregistered or unsupported objects may serialize by name only, compare loosely, or be skipped depending on `ConfigOptions`.

Error-path assertions are important because parsers should leave destination options unchanged on invalid input. Escaping and nested brace parsing are high-risk because options strings are embedded in OPTIONS files where comments, separators, CF names, and object config payloads can collide. The legacy API section duplicates much of the modern coverage and must remain aligned until those APIs are actually removed.

## Test Signals
The file is itself the test signal and is run as a gtest binary. Strong indicators are exact/loose verification status, round-trip equality, parser rejection of malformed OPTIONS files, object-registry creation success, `OptionTypeInfo` mismatch names, and `RUN_ALL_TESTS()` success. Good future regressions should include new option fields in map/string/serialization paths, persisted-version unknown-option behavior, and unchanged-destination checks for every new parser failure mode.
