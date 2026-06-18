# sources/storage-engines/tikv/components/codec/src/convert.rs

## Purpose
Provides bit-level conversions that turn signed integers and floating-point values into unsigned integers whose big-endian byte representation is memory-comparable.

## APIs and control flow
`encode_i64_to_comparable_u64` and `decode_comparable_u64_to_i64` XOR the sign bit (`1 << 63`), moving signed integer ordering into unsigned ordering. `encode_f64_to_comparable_u64` reads IEEE bits with `to_bits`; positive values set the sign bit, while negative values are bitwise inverted. `decode_comparable_u64_to_f64` reverses that transform before `from_bits`.

## State, dependencies, and integration
The module is pure and has no persistence or allocation. It is private to the codec crate and is consumed by `number.rs` for `i64` and `f64` ascending and descending encodings. The functions assume normal Rust `f64` bit semantics and preserve bit patterns through reversible transforms.

## Risks and test signals
NaN ordering is not defined by ordinary `PartialOrd`; the paired number codec tests intentionally exclude NaN. Signed zero is represented distinctly, and local tests verify `0.0` and `-0.0` encode differently. Tests also check integer sign-bit mapping and representative decode behavior.
