# sources/storage-engines/tikv/components/tidb_query_datatype/src/def/eval_type.rs

## Purpose
This file defines `EvalType`, the reduced set of runtime value categories used by TiKV expression and vectorized query execution. It maps TiDB/MySQL field types into execution categories such as `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Enum`, `Set`, and `VectorFloat32`.

## Important APIs, types, and functions
`EvalType` is a copyable enum with a debug-backed `Display` implementation. `into_certain_field_type_tp_for_test` maps each eval type to one representative `FieldTypeTp`, primarily for tests that need a concrete protobuf field type. `TryFrom<FieldTypeTp> for EvalType` is the production conversion surface. Integer-like MySQL types, including `Bit` and `Year`, map to `Int`; `Float` and `Double` map to `Real`; all date/time/timestamp field types map to `DateTime`; string and blob families plus `Null` map to `Bytes`; TiDB vector float32 maps to `VectorFloat32`.

## Control flow
Conversion is a single match over `FieldTypeTp`. Unsupported or not-yet-encoded types return `DataTypeError::UnsupportedType`; currently `Unspecified`, `NewDate`, `Set`, and `Geometry` fall into the error path even though `EvalType::Set` exists.

## State and persistence behavior
There is no mutable state or persistence. This module is pure type classification.

## Dependencies and integration points
The conversion depends on `FieldTypeTp` and `DataTypeError`. It is used by expression builders, aggregation executors, vector column allocation, and support checks to choose typed execution paths.

## Risks and edge cases
The existence of `EvalType::Set` but rejection of `FieldTypeTp::Set` is intentional per the TODO, but it can surprise new call sites. Timestamp is intentionally collapsed into `DateTime`, so any logic needing timestamp-specific timezone behavior must use field metadata elsewhere.

## Test signals
The test matrix exercises every major `FieldTypeTp` and verifies supported mappings versus unsupported errors.
