# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_string.rs

## Purpose

This file implements TiKV coprocessor RPN scalar functions for TiDB/MySQL string expressions. The functions are exported through `#[rpn_fn]` annotations and are evaluated by the `tidb_query_expr` expression engine against `Bytes`, `Int`, real, enum, and raw scalar arguments. The implementation covers byte-oriented string operations, UTF-8-aware variants, collation-aware comparisons/searches, base64/hex conversions, padding, trimming, substring extraction, quoting, and MySQL variadic functions such as `CONCAT`, `CONCAT_WS`, `FIELD`, `ELT`, and `MAKE_SET`.

The file deliberately separates binary/byte semantics from UTF-8 character semantics. Byte functions such as `left`, `right`, `substring`, `length`, `char_length`, and `reverse` work on raw byte positions and may split multibyte text. UTF-8 variants validate input with `str::from_utf8`, count Rust `char`s, and convert character offsets back to byte offsets before writing output.

## Important APIs, Types, and Functions

- `#[rpn_fn]`, `#[rpn_fn(writer)]`, `#[rpn_fn(nullable)]`, `#[rpn_fn(varg)]`, and `#[rpn_fn(raw_varg)]` register scalar functions with the TiKV RPN evaluator and determine argument nullability, variadic behavior, raw scalar access, and `BytesWriter` output handling.
- `BytesRef`, `Bytes`, `BytesWriter`, and `BytesGuard` are the main byte input/output contracts from `tidb_query_datatype::codec::data_type`.
- `Int` is the signed integer representation used by string functions that accept numeric lengths, positions, masks, or indices.
- `Collator` controls sort/search equality for collation-sensitive functions: `locate_2_args_utf8`, `locate_3_args_utf8`, `strcmp`, `field_bytes`, and `find_in_set`.
- `Encoding` supplies charset-specific case mapping for `upper_utf8` and `lower_utf8`; binary `upper` and `lower` intentionally return the original bytes unchanged.
- `ScalarValueRef` is used by raw variadic functions `make_set` and `elt` so the first argument can be interpreted as an integer while later arguments are interpreted as bytes.
- `elt_validator` enforces the raw variadic signature shape: first child returns `EvalType::Int`, remaining children return `EvalType::Bytes`.
- Helper constants define MySQL compatibility limits and formatting behavior: `SPACE`, `MAX_BLOB_WIDTH`, `BASE64_LINE_WRAP_LENGTH`, base64 chunk sizes, and newline wrapping.

Major function groups:

- Numeric/string conversions: `bin`, `oct_int`, `oct_string`, `hex_int_arg`, `hex_str_arg`, `unhex`, `ascii`, `ord`.
- Length and position: `length`, `bit_length`, `char_length`, `char_length_utf8`, `locate_2_args`, `locate_3_args`, UTF-8 locate variants, `instr`, `instr_utf8`.
- Concatenation and selection: `concat`, `concat_ws`, `field`, `field_bytes`, `make_set`, `elt`.
- Mutation/extraction: `replace`, `insert`, `insert_utf8`, `left`, `left_utf8`, `right`, `right_utf8`, byte and UTF-8 `substring` variants, `substring_index`.
- Whitespace/pattern operations: `ltrim`, `rtrim`, `trim_1_arg`, `trim_2_args`, `trim_3_args`, internal `trim`, `TrimDirection`.
- Padding/case/repetition: `lpad`, `lpad_utf8`, `rpad`, `rpad_utf8`, `upper`, `upper_utf8`, `lower`, `lower_utf8`, `space`, `repeat`.
- Encoding/escaping: `to_base64`, `from_base64`, `quote`, plus internal `line_wrap`, `encoded_size`, and `strip_whitespace`.

## Control Flow and Behavior

Most exported functions are small, pure transforms. Null propagation is mostly handled by the `rpn_fn` codegen layer according to each annotation, while nullable/raw functions handle `Option` values explicitly. Writer-based functions either call `writer.write_ref(Some(...))` to borrow an input slice, `writer.write(Some(Vec<u8>))` to return allocated data, or `writer.begin()` with `partial_write` when constructing output in pieces.

UTF-8 functions follow a common pattern: validate bytes with `str::from_utf8`, compute character counts or character start indices, then write byte slices or character iterators. `get_utf8_byte_index` is the central helper for converting a character index to a safe byte index. Byte-oriented variants instead index directly into slices and can produce partial multibyte sequences by design.

Search functions use `memchr::memmem` for efficient byte substring search. Case-insensitive UTF-8 locate lowercases both haystack and needle before search and uses a helper `find_str` to convert the found byte offset back into a character position. Collation-aware equality is delegated to `C::sort_compare`.

Padding functions delegate target-length validation to `validate_target_len_for_pad`. That helper returns `Some(0)` for a requested empty result, `None` for MySQL-compatible NULL cases such as negative target length, target size exceeding `MAX_BLOB_WIDTH`, or empty pad when extension would be required, and `Some(target_len)` otherwise. UTF-8 padding uses a `size_of_type` of 4 to guard worst-case byte expansion.

Base64 encoding checks blob limits and uses `encoded_size` with checked arithmetic before allocating. It encodes with `base64::STANDARD`, then mutates the output buffer in-place via `line_wrap` to insert MySQL-style newlines every 76 encoded characters. Decoding strips whitespace first, returns an empty byte string on overflow or invalid padding, and returns NULL only when the base64 crate rejects otherwise well-shaped input.

`substring` and `substring_utf8` share signed-position semantics through `i64_to_usize`: positive positions are 1-based, negative positions count backward from the end, position zero or nonpositive length returns empty output, and saturated/clamped arithmetic avoids index panics for extreme `i64` inputs.

## State and Persistence Behavior

The implementation is stateless. It does not mutate persistent storage, access the filesystem, or maintain global mutable state. All state is local to one scalar evaluation and consists of temporary slices, counters, vectors, and `BytesWriter` buffers. Persistence behavior is entirely indirect: results flow back through the TiKV coprocessor expression evaluation pipeline and may be returned to TiDB as query results.

Memory allocation is bounded in several places but not universally capped:

- `space`, `lpad`, `rpad`, and `to_base64` apply blob-width checks before large output construction.
- `repeat` caps counts above `i32::MAX` but does not explicitly compare final output length against `MAX_BLOB_WIDTH`.
- `concat`, `concat_ws`, `replace`, `quote`, and substring-related functions allocate proportional to input/output size, relying on upstream row/value limits and `BytesWriter` behavior.

## Dependencies and Integration Points

- `tidb_query_codegen::rpn_fn` is the primary integration point with generated RPN evaluator dispatch.
- `tidb_query_common::Result` and `box_err!` carry evaluation errors, notably invalid UTF-8 and invalid trim direction.
- `tidb_query_datatype::{codec::collation::*, data_type::*, *}` supplies collations, charsets, encodings, scalar value types, blob-width constants, and MySQL data type metadata.
- `crate::impl_math::i64_to_usize` is reused for signed/unsigned length and position conversion.
- `super::function::validate_expr_return_type` and `tipb::Expr` connect `elt_validator` to expression signature validation.
- External crates include `memchr` for substring search, `bstr::ByteSlice` for byte splitting by comma in `find_in_set`, `hex` for `UNHEX`, `base64` for base64 conversion, and `log_wrappers::hex_encode_upper` for uppercase byte hex encoding.
- The test module integrates through `RpnFnScalarEvaluator`, `FieldTypeBuilder`, `Collation`, charset constants, and `tipb::ScalarFuncSig`, which verifies the public dispatch signatures rather than only direct Rust calls.

## Risks and Edge Cases

- The UTF-8 `insert_utf8` implementation computes character counts but slices with `s.as_bytes()[0..upos - 1]` and `s.as_bytes()[upos + ulen - 1..]`; these are byte indices derived from character positions and can be wrong or panic for multibyte input. Existing tests only cover ASCII inputs for `insert_utf8`.
- Case-insensitive UTF-8 locate lowercases strings and then uses a byte offset from the lowercased string against the original string to count characters. Unicode case mapping can change byte length or character count, so this is risky for non-ASCII case-folding behavior.
- `instr_utf8` uses `String::from_utf8_lossy` instead of strict validation, so invalid UTF-8 behavior differs from stricter UTF-8 functions such as `left_utf8`, `right_utf8`, `char_length_utf8`, and `substring_utf8`.
- `repeat` can perform very large loops and produce very large buffers for large positive counts and nonempty inputs. It caps only the count, not the total byte size.
- `quote` preallocates `bytes.len() * 2 + 2`, which can overflow for pathological lengths if upstream limits are not already enforced.
- Binary `left`, `right`, `substring`, and `reverse` intentionally operate on bytes; callers must select UTF-8 variants when character-safe behavior is required.
- `ord` returns zero when no character can be decoded by the selected charset, which is MySQL-compatible but can hide malformed input if callers expect an error.
- The local `MAX_BLOB_WIDTH` is an `i32` with a FIXME, while `tidb_query_datatype::MAX_BLOB_WIDTH` is also referenced elsewhere; mismatched constants would create inconsistent limits.
- `trim` removes only full repeated pattern chunks from edges. This is intentional for MySQL-style pattern trim, but pattern lengths that do not align with the string edges can surprise maintainers expecting substring trimming.

## Test Signals

The `#[cfg(test)]` module is extensive and exercises nearly every exported scalar through `RpnFnScalarEvaluator` and `ScalarFuncSig`. It covers:

- Null propagation, empty strings, negative and zero lengths/positions, maximum/minimum integer positions, and blob-width limit cases.
- Byte vs UTF-8 distinction for length, left/right, substring, reverse, padding, and character counting.
- Collation behavior for locate, `FIELD` on strings, `STRCMP`, and `FIND_IN_SET`, including case-insensitive `Utf8Mb4GeneralCi`.
- Charset-specific upper/lower behavior for UTF-8, GBK, and GB18030 with nontrivial Unicode case mappings.
- Invalid UTF-8 behavior for locate UTF-8 variants, trim byte variants, and `char_length_utf8`.
- Base64 encoding line wrapping, whitespace-tolerant decoding, invalid base64 returning an empty string, and hex/unhex handling including odd-length inputs.
- MySQL-compatible edge behavior for `OCT`, `SPACE`, `MAKE_SET`, `ELT`, `SUBSTRING_INDEX`, `QUOTE`, and `REPEAT`.

Notable test gaps are `insert_utf8` with multibyte input and stress tests for large `repeat`, `concat`, `quote`, and replacement output sizes. Property-style tests comparing TiKV results with TiDB/MySQL for Unicode case folding and collation-sensitive search would also reduce risk.
