## sources/test-tools/syzkaller/pkg/image/compression_optimized.go

Purpose: optimized Unix-like decompressor for large sparse images, avoiding writes of zero words into an anonymous mmap.

Important APIs/types/functions: build tag `!windows && !386 && !arm`; `decompressScratch`, `decompressPool`, `pageSize`, and `mustDecompress`.

Control flow: reuses a pooled zlib reader/scratch buffer, mmaps a fixed `maxImageSize` buffer, reads zlib chunks, copies only non-zero words/trailing bytes, counts paged-in pages approximately, returns a slice trimmed to actual decompressed length and a destructor that updates stats and munmaps the full mapping.

State and persistence: uses `sync.Pool` and global `StatImages`/`StatMemory`. Mmap lifetime is tied to caller destructor.

Dependencies and integration: depends on `syscall.Mmap/Munmap`, `unsafe`, and the shared compressed-image API. `maxImageSize` must remain compatible with executor-side constants.

Risks: unsafe pointer arithmetic and word copying require careful bounds handling. Decompressed data larger than `132 << 20` panics. Leaked destructor calls leak virtual mappings and stats. The page accounting is intentionally approximate.

Test signals: shared tests confirm round-trip content; benchmark measures this path on supported hosts.
