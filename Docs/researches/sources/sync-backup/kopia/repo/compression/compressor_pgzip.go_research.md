# sources/sync-backup/kopia/repo/compression/compressor_pgzip.go

Purpose: registers parallel gzip variants using `github.com/klauspost/pgzip`.

Important APIs/types/functions: init registers `pgzip`, `pgzip-best-speed`, and `pgzip-best-compression`; `pgzipCompressor` owns header bytes and writer pool; `pgzipDecoderPool` reuses `pgzip.Reader` instances.

Control flow: compression writes the Kopia header, resets a pooled pgzip writer to output, streams input, closes to flush, and returns it. Decompression optionally verifies header, resets a pooled reader, copies output, and returns the reader.

State and persistence behavior: persisted payload is Kopia header plus gzip-compatible pgzip stream. Pools are in-memory only.

Dependencies/integration: registered in compression registry and benchmarked alongside other compressors.

Risks and edge cases: pgzip concurrency can affect CPU usage and output size. `mustSucceed` on reader reset assumes reset errors are impossible at that point.

Test signals: shared compressor tests and benchmarks cover round-trip, header mismatch, and performance behavior.
