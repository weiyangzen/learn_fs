# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionKey.java research

## Purpose

`MutableOptionKey` is the small internal interface that lets mutable-option builders treat enum constants from different option groups uniformly.

## Important APIs and types

`ValueType` enumerates the supported serialized types: `DOUBLE`, `LONG`, `INT`, `BOOLEAN`, `INT_ARRAY`, `ENUM`, and `STRING`. Implementers must provide `name()` and `getValueType()`. Java enums automatically provide `name()`, so option-key enums only implement value typing.

## Control flow

Abstract mutable-option builders use `name()` to serialize the native option key and `getValueType()` to parse or validate `MutableOptionValue` instances.

## State and persistence behavior

The interface has no state. It helps produce string key/value payloads that native RocksDB applies to live DB or column-family options.

## Dependencies and integration points

It is implemented by `MutableDBOptions.DBOption` and the option groups inside `MutableColumnFamilyOptions`. It works with `MutableOptionValue` and `AbstractMutableOptionsBuilder`.

## Risks and test signals

Adding a native mutable option requires selecting the correct `ValueType`; wrong typing can cause Java parse failures or native rejection. Tests should cover every value type and option-key group during parse/build and native application.
