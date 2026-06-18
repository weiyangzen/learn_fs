# sources/storage-engines/rocksdb/util/coding.cc

Purpose: provides out-of-line implementations for selected varint encoding and decoding functions declared in `coding.h`, keeping hot inline helpers in headers while centralizing fallback loops.

Important APIs and functions: `EncodeVarint32(char*, uint32_t)` emits one to five bytes using continuation bit `128`, with specialized branches for value ranges under 2^7, 2^14, 2^21, 2^28, and larger. `GetVarint32PtrFallback(const char*, const char*, uint32_t*)` decodes up to five bytes, returning nullptr on truncation or malformed overflow. `GetVarint64Ptr` decodes up to ten bytes by shifting seven bits at a time and returns nullptr on truncation or malformed data.

Control flow and state: all functions are stateless and operate on caller-provided byte ranges. Encode returns the first byte after the encoded value. Decode functions advance local pointers and only write output on successful termination.

Dependencies and integration: includes `util/coding.h` and RocksDB slice headers. `coding.h` inline functions call these from string append, slice parse, and pointer parse APIs.

Risks and test signals: callers must provide sufficient output space for encoders and correct input bounds for decoders. The 64-bit loop condition uses `shift <= 63` with increments of 7, allowing ten bytes while avoiding shifts beyond 63. `coding_test.cc` covers fixed encodings, varint round trips, overflow, truncation, length-prefixed strings, and prefix-varint helpers.
