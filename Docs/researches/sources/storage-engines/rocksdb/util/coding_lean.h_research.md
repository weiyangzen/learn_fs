# sources/storage-engines/rocksdb/util/coding_lean.h

Purpose: supplies a small, dependency-light subset of fixed-width little-endian encode/decode helpers. It is separated from `coding.h` for users that only need fixed integer serialization without slice and varint machinery.

Important APIs and functions: `EncodeFixed16`, `EncodeFixed32`, and `EncodeFixed64` write little-endian bytes into caller-provided buffers, using `memcpy` on little-endian platforms and manual byte extraction otherwise. `DecodeFixed16`, `DecodeFixed32`, and `DecodeFixed64` read little-endian bytes, using `memcpy` on little-endian platforms and manual reconstruction otherwise.

Control flow and state: all functions are inline, stateless, and perform no bounds checks. The caller must supply buffers of at least 2, 4, or 8 bytes as appropriate.

Dependencies and integration: depends on `<cstdint>`, `<cstring>`, and `port/port.h` for `port::kLittleEndian`. `coding.h`, comparator timestamp helpers, and Bloom tests use these primitives through fixed encoding APIs.

Risks and test signals: absence of bounds checks is intentional but places responsibility on callers. Endianness correctness is central to on-disk compatibility. `coding_test.cc` validates little-endian output and fixed integer round trips over broad value ranges.
