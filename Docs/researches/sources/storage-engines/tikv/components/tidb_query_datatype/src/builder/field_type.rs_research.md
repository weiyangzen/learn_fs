# sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/field_type.rs

## Purpose
Implements a fluent helper for constructing `tipb::FieldType` protobuf messages in tests and query datatype setup code.

## APIs, Flow, And State
`FieldTypeBuilder` wraps a `FieldType` and exposes chainable setters: `tp`, `flag`, `flen`, `decimal`, `collation`, and `charset`. Type, flag, length, decimal, and collation setters route through `FieldTypeAccessor` so enum/bit representations stay consistent with crate conventions. `charset` writes the protobuf string directly. `build` consumes the builder, and `From<FieldTypeBuilder> for FieldType` provides conversion ergonomics.

## Dependencies And Integration
Depends on `tipb::FieldType`, `FieldTypeAccessor`, `FieldTypeTp`, `FieldTypeFlag`, and `Collation`. It is re-exported by the builder module for callers needing compact schema construction.

## Risks And Test Signals
The builder is simple and has no persistence. Risk is mostly misuse: unset fields keep protobuf defaults, and `charset` bypasses accessor validation. Compile-time type checking and downstream field-type tests are the main signals.
