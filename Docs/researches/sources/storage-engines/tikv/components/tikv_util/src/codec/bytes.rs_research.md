# sources/storage-engines/tikv/components/tikv_util/src/codec/bytes.rs

Purpose: implements byte-slice encoders/decoders for TiKV's memcomparable byte format and a compact length-prefixed byte format.

Important APIs: `BytesEncoder` extends `NumberEncoder` with `encode_bytes(key, desc)` and `encode_compact_bytes(data)`. Free functions include `max_encoded_bytes_size`, `encode_bytes`, `encode_bytes_desc`, `encoded_compact_len`, `encoded_bytes_len`, `decode_compact_bytes`, `decode_bytes`, `decode_bytes_in_place`, and `is_encoded_from`. `CompactBytesFromFileDecoder` decodes compact bytes from `BufRead`.

Control flow: memcomparable encoding writes 8-byte groups followed by a marker `0xff - pad`; descending encoding bitwise-inverts payload, padding, and marker. Decoding reads 9-byte chunks until it sees padding, validates padding bytes, optionally inverts descending data, advances the input slice past the encoded key, or compacts a `Vec` in place with `ptr::copy`. Compact encoding writes a varint length then raw bytes.

State and persistence: no retained state. Encoded bytes are intended for persistent keys and sortable storage formats, while compact bytes trade orderability for smaller/faster serialization.

Dependencies and integration: uses `byteorder`, `std::io::Write/BufRead`, and number varint codecs. This format underpins key comparisons in TiKV/TiDB-compatible storage.

Risks: invalid chunk lengths, markers, or padding return `UnexpectedEof`/`KeyPadding`; `decode_bytes_in_place()` uses unsafe length and overlapping-copy operations; `encoded_*_len()` helpers intentionally do not fully validate encodings. Descending encoding must stay exactly symmetric.

Test signals: tests cover asc/desc encode-decode vectors, invalid encodings, order preservation/reversal, max-size calculation, compact codec including file decoder, and benchmarks for encode/decode/in-place/check helpers.
