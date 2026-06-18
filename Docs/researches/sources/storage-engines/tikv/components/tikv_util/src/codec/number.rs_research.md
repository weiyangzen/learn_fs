# sources/storage-engines/tikv/components/tikv_util/src/codec/number.rs

Purpose: implements ordered and non-ordered numeric encoders/decoders for integers and floating-point values used by TiKV key/value codecs.

Important APIs: constants for varint and fixed widths; `NumberEncoder` methods for ordered big-endian `i64`, `u64`, `u32`, `u16`, descending variants, protobuf-compatible varints, ordered `f64`, and little-endian primitive encodings. Decode functions mirror each format: `decode_i64`, `decode_u64_desc`, `decode_var_i64`, `decode_f64_le`, `read_u8`, and others.

Control flow: ordered signed integers flip the sign bit; ordered floats set the sign mark for positives and invert negatives so byte ordering matches numeric ordering. Descending encodings invert the ordered `u64`. Varint encoding writes 7-bit groups with continuation bits; decoding has fast paths for one-byte values and complete 10-byte windows, with overflow detection when the 10th byte exceeds 1.

State and persistence: no local state. Encoded forms are persisted inside keys, values, or protobuf-compatible compact structures by callers.

Dependencies and integration: uses `byteorder` read/write helpers and shared codec `Error/Result`. `bytes.rs` depends on varint length encoding and fixed-width timestamp-compatible encodings.

Risks: float ordering excludes NaN from tests and uses `partial_cmp().unwrap()` in order checks; varint decoding uses unsafe unchecked indexing after guarding lengths, so guard correctness is important. Little-endian encodings are not memcomparable.

Test signals: macro-generated tests cover serialization and order for integer/float codecs, little-endian round trips, varint compatibility with protobuf `CodedOutputStream`, EOF/write-zero handling, overflow, and incomplete varint errors.
