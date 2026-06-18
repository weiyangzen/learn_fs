# sources/sync-backup/kopia/repo/compression/compressor_zstd.go

Purpose: registers Zstandard compressor variants using `klauspost/compress/zstd`.

Important APIs/types/functions: init registers `zstd`, `zstd-fastest`, `zstd-better-compression`, and deprecated `zstd-best-compression`; `zstdCompressor` implements common compressor methods; `zstdDecoderPool` reuses single-concurrency decoders.

Control flow: compression writes header, takes/resets a pooled zstd encoder, streams input, closes to flush, and returns it. Decompression optionally verifies the header, resets a pooled decoder on input, copies decoded bytes, and returns the decoder after resetting to nil.

State and persistence behavior: compressed content carries a Kopia header that selects the zstd level variant. Best-compression remains readable but marked deprecated for new selection behavior.

Dependencies/integration: registered in global compression maps and frequently used as metadata compressor in repository tests.

Risks and edge cases: decoder reset errors are returned; encoder creation errors panic through `mustSucceed` during pool initialization. Deprecated status affects UI/selection but not read compatibility.

Test signals: compressor tests and content formatter tests exercise zstd round-trips and repository read/write paths.
