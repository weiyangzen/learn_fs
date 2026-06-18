# sources/storage-engines/rocksdb/util/coding.h

Purpose: declares and implements RocksDB's canonical byte-order-independent serialization helpers for fixed-width integers, varints, signed zigzag varints, length-prefixed slices, delimiter slicing, and unaligned memory access.

Important APIs and types: fixed writers `PutFixed16/32/64` append little-endian values to strings, while `EncodeFixed*` and `DecodeFixed*` come from `coding_lean.h`. Varint APIs include variadic `PutVarint32`, `PutVarint64`, combined append helpers, `EncodeVarint32/64`, `GetVarint32/64`, pointer decoders, and `VarintLength`. Signed values use `i64ToZigzag`, `zigzagToI64`, `PutVarsignedint64`, and `GetVarsignedint64`. Slice helpers include `PutLengthPrefixedSlice`, `PutLengthPrefixedSliceParts`, padding variants, `GetLengthPrefixedSlice`, and `GetSliceUntil`. `PutUnaligned` and `GetUnaligned` abstract platforms that disallow unaligned access.

Control flow and state: functions are stateless transformations on strings, slices, and byte pointers. `Get*` functions advance `Slice` inputs only on success. The unchecked `GetLengthPrefixedSlice(const char*)` assumes well-formed data and limits varint parsing to five bytes.

Dependencies and integration: includes `port/port.h`, `rocksdb/slice.h`, `util/cast_util.h`, and `util/coding_lean.h`. This file is broadly integrated across table formats, keys, options, metadata, and filter tests.

Risks and test signals: many lower-level APIs require callers to allocate enough output space and provide valid data. Length-prefixed slice sizes are cast to `uint32_t`, so callers must not encode slices larger than that contract. Unaligned helpers depend on compile-time platform detection. `coding_test.cc` gives strong boundary coverage for fixed encodings, varints, truncation, overflow, strings, and prefix-varint behavior.
