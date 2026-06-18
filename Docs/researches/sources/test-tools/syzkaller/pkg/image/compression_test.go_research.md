## sources/test-tools/syzkaller/pkg/image/compression_test.go

Purpose: validates compression/base64 helpers and provides a decompression benchmark.

Important APIs/types/functions: `TestCompress`, `TestEncode`, and `BenchmarkDecompress`.

Control flow: tests compress/decompress representative byte slices, call destructors, compare with originals, and verify base64 encode/decode round trips. Benchmark repeatedly calls `MustDecompress` on a compressed sample and destroys each result.

State and persistence: no persistent state.

Dependencies and integration: imports package as `image_test`, exercising public API only.

Risks: tests cover happy-path round trips but not malformed zlib, destructor leaks, optimized max-size overflow, or stat accounting.

Test signals: strong smoke signal for data preservation across build-tagged decompressor implementations.
