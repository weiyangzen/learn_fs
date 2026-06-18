# sources/storage-engines/rocksdb/util/coding_test.cc

Purpose: tests fixed integer encoding, legacy varint encoding, length-prefixed string parsing, and prefix-varint helpers. It is the main regression suite for serialization primitives used throughout RocksDB formats.

Important tests and helpers: `Fixed16`, `Fixed32`, and `Fixed64` perform round trips over large value sets and powers-of-two boundaries. `EncodingOutput` asserts little-endian byte order. `Varint32` and `Varint64` round-trip many boundary values and verify encoded length. Overflow and truncation tests verify malformed varints return nullptr. `Strings` checks length-prefixed slices. Prefix-varint helper traits abstract over 32- and 64-bit APIs, while tests validate exact byte strings, split disk-read decode APIs, invalid additional-byte counts, overflow, truncation, and `EncodePrefixVarint64<kMinimumBytes>` improper/minimum-width encodings.

Control flow and state: tests build encoded strings, decode by pointer and `Slice`, and assert input exhaustion. Prefix-varint tests keep helper cases close to expected byte strings, creating a schema-style compatibility lock.

Dependencies and integration: includes `util/coding.h`, RocksDB test harness, and `util/prefix_varint.h`. `main` installs stack traces and runs GoogleTest.

Risks and test signals: this suite is high-signal for serialization compatibility and malformed-input handling. It does not directly test `PutUnaligned/GetUnaligned`, `GetSliceUntil`, or oversized length-prefix caller contracts. Prefix-varint coverage in this file means changes to `prefix_varint.h` can break this coding test even though that header is outside the work item.
