# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/binary_literal.rs

## Purpose
Implements MySQL bit and hexadecimal literal handling. `BinaryLiteral` stores raw bytes and provides parsing, formatting, ordering, bit-string rendering, and unsigned-integer conversion with TiDB/MySQL truncation behavior.

## Important APIs, Types, And Functions
- `BinaryLiteral(Vec<u8>)`: internal byte-backed representation for bit and hex literals.
- `trim_leading_zero_bytes`: normalizes byte slices for comparison and integer conversion while preserving a single zero byte for all-zero inputs.
- Free `to_uint(ctx, bytes)`: converts big-endian bytes to `u64`, reporting truncation through `EvalContext` when more than 8 significant bytes remain.
- `BinaryLiteral::from_u64`: creates a big-endian literal with requested byte width or trimmed width.
- `from_hex_str`: parses `x'...'`, `X'...'`, and `0x...` forms.
- `from_bit_str`: parses `b'...'`, `B'...'`, and `0b...` forms into bytes, padding to byte boundaries.
- `to_bit_string`: renders `b'...'`, optionally trimming leading zero bits.
- `to_uint`, `Display`, `Eq`, `Ord`, `PartialEq`, and `PartialOrd`.

## Control Flow
Hex parsing validates the prefix, strips quote wrappers for `x'...'`, rejects odd-length quoted hex, and pads odd-length `0x...` input with a leading zero before decoding. Bit parsing validates the prefix, pads the bit stream to a byte boundary, then converts each 8-bit group with `usize::from_str_radix`. Integer conversion trims leading zero bytes, returns zero for empty input, signals truncation for more than eight significant bytes, and otherwise folds bytes in big-endian order. Ordering trims leading zeros, compares significant lengths, then compares bytes lexicographically.

## State And Persistence Behavior
No external persistence. The type owns bytes in memory. Its externally visible persistence form is string formatting (`0x...` or `b'...'`) and numeric conversion.

## Dependencies And Integration Points
Used by MySQL literal parsing and expression evaluation paths. It depends on the crate codec `Result`/`Error`, `EvalContext` for truncation handling, and the `hex` crate for decoding/encoding.

## Risks And Edge Cases
- `from_hex_str` accepts lowercase `0x` but not uppercase `0X`, matching the local tests but worth checking against parser expectations.
- Quoted hex literals must have an even number of digits; unquoted `0x...` odd lengths are padded.
- `from_bit_str` error messages for invalid prefixes mention hexadecimal format in one branch, which is misleading.
- `to_uint` returns `u64::MAX` after calling `handle_truncate_err`; depending on SQL mode, that call may produce an error instead.
- Formatting an empty literal displays as an empty string, while bit-string rendering displays `b''`.

## Test Signals
Local tests cover zero trimming, `from_u64` sizing, display formatting, hex parsing and invalid forms, bit parsing and invalid forms, bit-string rendering with and without trimming, unsigned conversion/truncation, and ordering with leading zeros.
