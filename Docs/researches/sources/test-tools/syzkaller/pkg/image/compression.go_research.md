## sources/test-tools/syzkaller/pkg/image/compression.go

Purpose: provides zlib compression/decompression and base64 helpers for syzkaller image data.

Important APIs/types/functions: `Compress`, `MustDecompress`, `DecompressCheck`, `DecodeB64`, `EncodeB64`, and internal `decompressWriter`. `StatImages` and `StatMemory` are atomics maintained by optimized decompression.

Control flow: `Compress` writes all bytes through a zlib writer and panics on unexpected writer errors. `MustDecompress` handles empty data specially then delegates to platform-specific `mustDecompress`. `DecompressCheck` streams decoded data to `io.Discard`. Base64 helpers use streaming encoders/decoders.

State and persistence: no persisted files. Global stats track optimized live decompressed images and estimated memory.

Dependencies and integration: uses `compress/zlib`, `encoding/base64`, and platform-specific files selected by build tags. Consumers must call the destructor returned by `MustDecompress` to release memory or locks.

Risks: `MustDecompress` panics on invalid data through backend implementations, so untrusted input should use `DecompressCheck` first. Forgetting the destructor leaks mmaps or holds the nonoptimized mutex.

Test signals: `compression_test.go` round-trips zlib and base64 data and benchmarks decompression.
