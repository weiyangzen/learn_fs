# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_vec.rs

## Purpose

`impl_vec.rs` implements TiDB vector scalar functions for the RPN expression engine. It provides text conversion, dimension counting, L1/L2 distances, negative inner product, cosine distance, and L2 norm for `VectorFloat32` values. Each function is annotated with `#[rpn_fn]`, so the codegen layer emits metadata consumed by `lib.rs` for `ScalarFuncSig::Vec*` dispatch.

## Important APIs, types, and functions

The core functions are small wrappers around `VectorFloat32Ref` methods:

- `vec_as_text(a, writer)` converts a vector to its textual representation and writes it through `BytesWriter`.
- `vec_dims(arg)` returns `arg.len()` as TiDB `Int`.
- `vec_l1_distance(a, b)` calls `a.l1_distance(b)?`.
- `vec_l2_distance(a, b)` calls `a.l2_distance(b)?`.
- `vec_negative_inner_product(a, b)` calls `a.inner_product(b)?` and negates the result.
- `vec_cosine_distance(a, b)` calls `a.cosine_distance(b)?`.
- `vec_l2_norm(a)` calls `a.l2_norm()`.

Distance and norm results are wrapped with `Real::new(...).ok()`. The comment explains the reason: TiKV does not support NaN as a SQL `Real`, so NaN converts to `NULL`. Infinite values are accepted when `Real::new` permits them, which is covered by tests with very large components.

## Control flow and error handling

There is no complex control flow. The binary distance functions delegate dimension checks and numeric computation to the vector datatype implementation. A mismatched vector length propagates as an error from the datatype method. Nullable behavior is mostly provided by the generated `rpn_fn` adapter: tests show that `NULL` vector operands produce `NULL` results for distance functions without entering the body with invalid references.

The writer function `vec_as_text` writes `Some(Bytes::from(a.to_string()))` to the output arena and returns a `BytesGuard`. Numeric functions return `Result<Option<Real>>` or `Result<Option<Int>>`, matching SQL nullability.

## State and persistence behavior

The file has no persistent state and no mutable global state. All behavior is pure with respect to vector inputs except for writing text results into the provided `BytesWriter`. Errors and nulls are returned directly through the RPN evaluation result path.

## Dependencies and integration points

The file depends on `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and `tidb_query_datatype::codec::data_type::*` for `VectorFloat32Ref`, `VectorFloat32`, `Bytes`, `BytesWriter`, `BytesGuard`, `Int`, and `Real`. It integrates with the crate-level dispatcher in `lib.rs`, which maps `ScalarFuncSig::VecAsTextSig`, `VecDimsSig`, `VecL1DistanceSig`, `VecL2DistanceSig`, `VecNegativeInnerProductSig`, `VecCosineDistanceSig`, and `VecL2NormSig` to the generated metadata functions.

## Risks and edge cases

The main correctness risks are numeric edge cases and consistency with TiDB's vector semantics. NaN is intentionally translated to `NULL`, notably for cosine distance involving zero vectors or overflow patterns. Dimension mismatch must continue to be an error rather than `NULL`. Very large `f32` values can produce infinities, and the tests show expected infinite `Real` values for L1/L2 distance and negative inner product. Since the implementation delegates to datatype methods, future changes in vector distance definitions will flow through here.

## Test signals

Tests cover dimensions for empty and non-empty vectors, L2 norm, L1/L2 distance, negative inner product, cosine distance, null operands, dimension mismatch errors, NaN-to-NULL behavior, and overflow to infinity. The cases are ported from pgvector expected output, giving a useful compatibility signal for common vector database semantics.
