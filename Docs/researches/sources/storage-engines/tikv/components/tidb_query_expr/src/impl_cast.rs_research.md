# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_cast.rs

## Purpose

This file implements TiKV coprocessor RPN cast expression dispatch and the concrete cast functions for TiDB-compatible scalar evaluation. It translates TiDB/TiPB field-type pairs into generated `RpnFnMeta` handlers, then provides conversion implementations across TiKV eval types: integer, real, decimal, bytes/string, date/time, duration, JSON, enum, set, vector-float32, and binary collation conversion.

The code is part of the query expression layer, not storage persistence. Its job is to make pushed-down SQL casts behave like TiDB/MySQL inside TiKV evaluation, including `UNSIGNED`, `YEAR`, `BIT`, binary literal, JSON parse flags, fractional-second precision, field length, charset/collation, warning, truncation, overflow, and `IN UNION` semantics.

## Important APIs, Types, and Functions

- `get_cast_fn_rpn_meta(is_from_constant, from_field_type, to_field_type) -> Result<RpnFnMeta>` is the central dispatch table. It converts TiPB `FieldType` type codes into `EvalType`, matches `(from, to)`, then selects a generated `*_fn_meta()` function emitted by `#[rpn_fn]`.
- `get_cast_fn_rpn_node(is_from_constant, from_field_type, to_field_type) -> Result<RpnExpressionNode>` wraps the selected metadata into an `RpnExpressionNode::FnCall` with one argument and default `tipb::InUnionMetadata`. This is used for internal TiKV-inserted casts.
- `map_cast_func(expr: &Expr) -> Result<RpnFnMeta>` maps pushed-down cast scalar functions from TiPB expressions. It validates exactly one child, detects whether the child is constant via `RpnExpressionBuilder::is_expr_eval_to_scalar`, and delegates to `get_cast_fn_rpn_meta`.
- `#[rpn_fn]` functions are the executable cast implementations. The macro also produces the `*_fn_meta()` factories used by the dispatcher. Attributes declare nullability and captured runtime inputs such as `ctx`, `extra`, `args`, and `metadata`.
- `EvalContext` carries SQL-mode-like behavior, time zone/test config, warning collection, and handlers such as `handle_overflow_err`, `handle_truncate_err`, and `handle_invalid_time_error`.
- `RpnFnCallExtra` provides the return `FieldType`, which controls unsignedness, field length, decimal precision/FSP, target time type, charset, and collation.
- `tipb::InUnionMetadata` controls special `UNION` casting behavior: several negative-to-unsigned casts clip to zero when `in_union` is true.
- Generic helpers `cast_any_as_any`, `cast_any_as_string`, `cast_any_as_decimal`, `cast_any_as_json`, `cast_any_as_bytes`, and `cast_json_as_any` delegate to TiKV datatype `ConvertTo`/`ConvertFrom` traits for common paths.

## Cast Families

Integer and unsigned integer casts include special paths for signed-to-unsigned, real-to-uint, string-to-int, binary-string-to-int, decimal-to-uint, JSON-to-uint, enum-to-int, and set-to-int. `cast_string_as_int` is especially involved: it validates UTF-8 prefixes, trims, handles negative unsigned `UNION` clipping, parses valid integer prefixes as signed or unsigned, appends warnings for signed overflow or negative-to-unsigned conversions, and maps parse overflows to clipped boundaries.

Real casts cover signed/unsigned integer to real, real-to-real, string/binary string to real, decimal-to-unsigned-real, JSON-to-real through generic conversion, and enum-to-real. String inputs go through TiDB-style float-prefix conversion and `produce_float_with_specified_tp` so return field length, decimal scale, and unsigned clipping can produce the expected warnings.

String/bytes casts use `cast_as_string_helper`, which calls `produce_str_with_specified_tp` and then pads binary string targets with zeros. Specialized paths preserve MySQL/TiDB details: `YEAR` zero becomes `"0000"`, `BIT` serializes as big-endian bytes trimmed to target `flen`, unsigned ints format through `u64`, float uses `f32` formatting for source `FLOAT`, JSON converts through JSON stringification, vector-float32 uses its textual representation, and enum uses the enum name.

Decimal casts combine source conversion with `produce_dec_with_specified_tp`. There are specialized unsigned source/target paths for signed int, real, string, and decimal that may zero negative values under `in_union`; otherwise generic decimal production enforces precision, scale, DML flags, overflow, and truncation behavior.

Duration casts route integer values through `Duration::from_i64`; real, bytes, decimal, and JSON use string-like parsing via `cast_bytes_like_as_duration`; time casts convert `DateTime` to `Duration`; duration-to-duration rounds FSP. Overflow and truncation codes are converted into context warnings and `NULL` results where applicable.

Date/time casts parse or transform integers, years, reals, strings, decimals, existing times, durations, enums, and JSON. Target `FieldTypeTp` and fractional seconds come from `extra.ret_field_type`. Invalid time errors are generally handled through `EvalContext` and returned as `NULL` if the context permits warning behavior. Duration-to-time depends on context time configuration because it constructs a time from a duration relative to a current/test timestamp.

JSON casts include bool-as-json, uint-as-json, generic scalar-to-json, string/enum-as-json, JSON identity, and JSON-to-scalar conversions. `cast_string_as_json` inspects the argument field type: binary string-like inputs become JSON opaque values, fixed-length binary strings are zero-padded to `flen`, `PARSE_TO_JSON` return flags parse the UTF-8 string as JSON syntax, and otherwise the bytes are treated as a JSON string with an unsafe UTF-8 assumption noted by a FIXME.

Collation conversion helpers `to_binary<E: Encoding>` and `from_binary<E: Encoding>` use the selected encoding implementation to encode/decode bytes for charset conversion.

## Control Flow

The runtime path starts with either TiKV internal cast insertion or TiPB scalar-function mapping. Both paths select an `RpnFnMeta` by matching source and target eval types plus field flags. The matcher includes many flag-sensitive branches, for example:

- binary string constants use binary literal numeric casts instead of normal string numeric parsing;
- source `YEAR`, `BIT`, `FLOAT`, bool, unsigned integer, enum, and vector types choose specialized handlers;
- target unsignedness chooses different integer, real, decimal, and JSON behavior;
- target JSON `PARSE_TO_JSON` and binary-string argument metadata affect string-to-JSON semantics.

During evaluation, each `#[rpn_fn]` receives nullable input and any captured context. Most functions return `Ok(None)` for SQL `NULL` or invalid/truncated values that are downgraded to warnings. Functions that need target metadata consult `extra.ret_field_type`; functions that need SQL mode or warnings mutate `EvalContext`; functions that need `UNION` behavior consult `InUnionMetadata`.

Shared conversion helpers reduce duplication, but important casts bypass the generic `ConvertTo` paths when MySQL/TiDB behavior requires custom clipping, rounding, parsing, warning codes, or opaque JSON handling.

## State and Persistence Behavior

This file does not persist data and owns no durable state. State effects are limited to the current expression evaluation:

- `EvalContext.warnings` is mutated to record overflow, truncation, data-too-long, and unknown warning codes.
- `EvalContext` flags decide whether errors are warnings or hard failures and whether values are clipped to zero in DML-like contexts.
- Return `FieldType` metadata controls output formatting and rounding for the current call only.
- `tipb::InUnionMetadata` is per-expression-call metadata and changes clipping behavior without global side effects.
- Some time conversions read context time zone/test configuration but do not write persistent state.

## Dependencies and Integration Points

The file depends heavily on `tidb_query_datatype::codec::convert` for `ConvertTo`/`ConvertFrom`, `produce_*_with_specified_tp`, valid-prefix parsing, binary literal conversion, and MySQL-compatible datatype implementations. It uses `tidb_query_datatype::expr::EvalContext` for SQL evaluation policy and warnings, and TiPB `Expr`/`FieldType`/`InUnionMetadata` for pushed-down expression metadata.

Integration with the RPN engine is through `RpnExpressionNode`, `RpnFnMeta`, `RpnFnCallExtra`, `RpnStackNode`, and `RpnExpressionBuilder`. The `tidb_query_codegen::rpn_fn` macro is essential: it binds Rust functions to scalar function metadata and generated evaluator shims. Tests use `RpnFnScalarEvaluator` and `tipb::ScalarFuncSig` to exercise the same dispatch path used by pushed-down coprocessor expressions.

The code also integrates with charset/collation encoding via `collation::Encoding`, byte ordering via `byteorder::BigEndian`, and MySQL temporal constants/types such as `Time`, `Duration`, `MAX_YEAR`, `MIN_YEAR`, `MAX_FSP`, and `TimeType`.

## Risks and Edge Cases

Several comments call out known compatibility gaps with MySQL or TiDB. Real-to-unsigned behavior intentionally preserves a questionable MySQL/TiDB-compatible boundary case. Negative-to-unsigned real and decimal casts have FIXME comments, especially outside `UNION`. String-to-int overflow warning selection is noted as not fully aligned with TiDB/MySQL in some cases. JSON stringification of floating values is also documented as not exactly matching TiDB formatting.

The dispatch table is broad and flag-sensitive; adding a new `EvalType`, `FieldTypeTp`, or cast signature can silently fall into `Unsupported cast` unless this matcher and tests are updated. Binary literal handling depends on both `is_from_constant` and binary-string-like field metadata, so planner changes in TiDB or expression constant detection can affect semantics.

String and JSON conversions are sensitive to UTF-8 handling. Normal numeric string casts validate prefixes, but `cast_string_as_json` has an unsafe UTF-8 branch when not parsing JSON and not treating input as binary opaque. The file explicitly notes missing JSONBinary parity for non-UTF-8 bytes.

Temporal casts are sensitive to target type, FSP rounding, invalid time policy, context flags, and time zone/test configuration. Duration-to-time can produce context-dependent results. Many invalid temporal inputs become warnings plus `NULL`, which must remain consistent with TiDB SQL modes.

Decimal production depends on precision/scale, unsigned flags, DML flags, and `produce_dec_with_specified_tp`; regressions here can change warning counts as well as numeric values. The test helper compares cast behavior to decimal production, but several TODOs note missing failure cases such as `Decimal::round` or `Decimal::from_f64` errors.

## Test Signals

The embedded test module is extensive and acts as the primary behavioral specification. It defines helpers for nullable inputs, metadata, field-type construction, warning validation, decimal/string/duration matrix testing, and RPN evaluator-based dispatch.

Coverage includes:

- integer, unsigned integer, set, enum, real, decimal, string, duration, time, JSON, vector, and binary charset cast families;
- `NULL` propagation for most nullable casts;
- `in_union` clipping of negative values to zero for unsigned targets;
- overflow and truncation warning codes under `OVERFLOW_AS_WARNING` and `TRUNCATE_AS_WARNING`;
- DML context flags for decimal clipping and warning behavior;
- binary literal integer/real conversions and binary string to JSON opaque values;
- field length, charset, collation, zero padding, and data-too-long behavior for string results;
- temporal parsing from int, year, real, string, decimal, duration, enum, and JSON with FSP rounding and invalid-input warnings;
- JSON parse-vs-string-vs-opaque modes, bool/uint JSON construction, and JSON scalar/object/array conversions;
- `to_binary`/`from_binary` charset examples for `utf8mb4`, `gbk`, and `gb18030`.

The most useful regression command for this file would be the TiKV Rust test target containing `tidb_query_expr::impl_cast` tests, or a filtered cargo invocation for `impl_cast`/cast tests in the `components/tidb_query_expr` crate. No tests were run for this research note.
