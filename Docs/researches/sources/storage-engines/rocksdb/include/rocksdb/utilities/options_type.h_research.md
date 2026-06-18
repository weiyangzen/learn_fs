# sources/storage-engines/rocksdb/include/rocksdb/utilities/options_type.h

## Purpose
Public metadata framework for parsing, serializing, comparing, preparing, and validating RocksDB option fields and custom extension option structs.

## Important APIs, Types, And Functions
`OptionType`, `OptionVerificationType`, `OptionTypeFlags`, callback aliases, and `OptionTypeInfo` are central. Factory helpers include `Enum`, `Struct`, `Array`, `Vector`, `StringMap`, `AsCustomSharedPtr`, `AsCustomUniquePtr`, and `AsCustomRawPtr`. Static helpers include `ParseType`, `SerializeType`, `TypesAreEqual`, `Find`, `NextToken`, and `StripOuterBraces`.

## Control Flow, State, And Persistence
Each `OptionTypeInfo` stores an offset into an option object plus callbacks/flags. `Parse` mutates the field at that offset, `Serialize` emits option-file strings, `AreEqual` applies sanity/verification rules, and prepare/validate hooks initialize or check nested configurable values. Arrays/vectors tokenize with brace-aware separators. Metadata is generally static; parsed option structs are caller-owned.

## Dependencies And Integration Points
Depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyOptions`, `Status`, `Slice`, and STL containers. It underpins options-file parsing, compatibility checks, custom configurable objects, and object-registry-backed extension construction.

## Risks And Edge Cases
Offset metadata is unsafe if it does not match actual struct layout. Deprecated and alias options parse differently from serialize/compare behavior. Pointer flags must match actual ownership. Brace tokenization, nested structs, and separator escaping are subtle. `ignore_unsupported_options` can selectively hide unsupported vector/array elements.

## Test Signals
Cover enum failures, struct field parsing, arrays/vectors, nested braces, string-map hex round trips, custom pointer reset, sanity-level comparisons, mutable-only parsing, prepare/validate hooks, and deprecated/alias behavior.
