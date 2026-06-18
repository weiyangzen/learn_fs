## sources/test-tools/syzkaller/pkg/image/compression_nonoptimized.go

Purpose: fallback decompressor for Windows, 386, and ARM where mmap/unsafe optimized decompression is not used.

Important APIs/types/functions: build tag `windows || 386 || arm`, package mutex `decompressMu`, and `mustDecompress`.

Control flow: locks globally, decompresses into a `bytes.Buffer` through `decompressWriter`, returns the bytes and `decompressMu.Unlock` as destructor.

State and persistence: global mutex serializes decompression to limit peak memory use. No persistent state.

Dependencies and integration: implements the backend required by `compression.go`.

Risks: callers must invoke the returned destructor or all future decompressions will block. Full decompression into memory can be expensive for large images.

Test signals: shared compression tests exercise this implementation only on matching build targets.
