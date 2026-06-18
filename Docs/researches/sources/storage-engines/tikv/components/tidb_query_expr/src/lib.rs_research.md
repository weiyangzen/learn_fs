# sources/storage-engines/tikv/components/tidb_query_expr/src/lib.rs

## Purpose

`lib.rs` is the root of the `tidb_query_expr` crate. It declares the expression implementation modules, re-exports public expression types, imports all generated RPN function metadata, and implements the central mapping from TiDB protobuf scalar function signatures (`tipb::ScalarFuncSig`) to executable `RpnFnMeta`. This is the crate-level dispatch table that lets pushed-down TiDB expressions run inside TiKV's coprocessor/vectorized query engine.

The crate documentation states the broader role: scanning and understanding TiDB rows, running pushed-down executors, returning execution results through the TiKV coprocessor interface, and exporting standalone UDF-like scalar functions.

## Important APIs, types, and functions

Module declarations expose `types` and implementation modules including arithmetic, cast, compare, control, encryption, JSON, LIKE, math, miscellaneous, op, regexp, string, time, and vector functions. `pub use self::types::*` makes RPN expression types available to downstream crates.

The helper mappers select specialized `RpnFnMeta` values based on field metadata:

- `map_to_binary_fn_sig` and `map_from_binary_fn_sig` choose charset-specialized binary conversion functions.
- `map_string_compare_sig`, `map_compare_in_string_sig`, `map_regexp_*`, `map_locate_*_utf8_sig`, `map_strcmp_sig`, `map_find_in_set_sig`, `map_ord_sig`, and `map_field_string_sig` choose collation-specialized string functions.
- `map_like_sig` selects both collation and charset behavior for SQL `LIKE`, using target/pattern charset compatibility to avoid incorrect `_` matching when TiDB has not pushed complete collation information.
- `map_int_sig` and `map_rhs_int_sig` inspect child `FieldTypeFlag::UNSIGNED` flags and select signed/unsigned arithmetic, comparison, division, modulo, and truncation implementations.
- `map_unary_minus_int_func`, `map_upper_utf8_sig`, and `map_lower_utf8_sig` validate arity and choose metadata based on signedness or charset.

`map_expr_node_to_rpn_func(expr)` is the large `ScalarFuncSig` match. It maps every supported pushed-down scalar signature to generated metadata, including the time functions from `impl_time.rs` and vector functions from `impl_vec.rs`. Unsupported signatures return an `other_err!("ScalarFunction ... is not supported in batch mode")`.

## Control flow and dispatch behavior

The dispatch path is: read the protobuf `Expr`, inspect `expr.get_sig()`, inspect child field types or return field type where needed, choose a generated `RpnFnMeta`, and return it to expression building. Some signatures map directly to a metadata function. Others go through helper mappers so runtime evaluation gets a monomorphized implementation matching unsigned integer combinations, charset/collation, return type, interval metadata, or argument count.

The match is organized by implementation module. It covers arithmetic, casts including vector casts, comparison and `IN`, control flow, encryption, JSON, vector functions, LIKE/regexp, math, miscellaneous functions, boolean/bit ops, string functions, and time functions. The time section wires many `ADDDATE`/`SUBDATE` variants to generic metadata functions with concrete type parameters, which must align exactly with TiDB planner signatures.

## State and persistence behavior

`lib.rs` does not store persistent state. It is a pure mapping layer from protobuf expression metadata to function metadata. The selected `RpnFnMeta` may carry function-specific metadata mappers that later build boxed metadata, but this file itself only chooses the function. Errors are returned as `tidb_query_common::Result`.

## Dependencies and integration points

This file depends on TiDB/TiKV datatype metadata (`Charset`, `Collation`, `FieldTypeAccessor`, `FieldTypeFlag`, collator templates, and datatype aliases), `tipb::{Expr, FieldType, ScalarFuncSig}`, and the generated metadata functions from every `impl_*` module. It is tightly coupled to:

- `RpnExpressionBuilder`, which calls this mapper when converting protobuf expression trees to RPN nodes.
- `tipb` signature definitions generated from TiDB protobufs.
- `tidb_query_codegen::rpn_fn`, which creates the `*_fn_meta()` functions referenced here.
- `tidb_query_datatype` field flags, charset, collation, and eval type semantics.

## Risks and edge cases

This file is a high-blast-radius compatibility table. Adding a new scalar function requires both an implementation and a correct mapping here. Incorrect signedness mapping can silently change overflow or comparison behavior. Incorrect collation mapping can produce wrong string comparisons, `LIKE`, regexp, `FIELD`, `FIND_IN_SET`, or `ORD` results. The `map_like_sig` compatibility branch is especially sensitive because it compensates for incomplete collation pushdown from TiDB.

The time and vector entries show how new function families are integrated. The vector mappings are direct and low-risk, but they require `ScalarFuncSig` names to stay synchronized. The time `ADDDATE`/`SUBDATE` mappings are riskier because many signatures share generic wrappers with type parameters; a single wrong type parameter can parse inputs using the wrong conversion trait or return a wrong SQL type.

## Test signals

This file has no local test module in the read content, so coverage is mostly indirect. Every implementation module's `RpnFnScalarEvaluator` tests relies on this dispatch mapping when evaluating by `ScalarFuncSig`. The `impl_time.rs` tests also build real protobuf expression trees for interval and timestamp-diff cases, giving stronger coverage for metadata mappers and dispatch alignment. `impl_vec.rs` tests cover the direct vector signature mappings through scalar evaluation. Remaining risk is for signatures not exercised by nearby module tests and for newly added `tipb::ScalarFuncSig` variants that fall into the unsupported default.
