# sources/sync-backup/kopia/repo/compression/compressor_deflate.go

Purpose: registers deflate compressor variants using `klauspost/compress/flate`.

Important APIs/types/functions: init registers `deflate-best-speed`, `deflate-default`, and `deflate-best-compression`; `newDeflateCompressor` builds a pooled writer; `deflateCompressor` implements `HeaderID`, `Compress`, and `Decompress`.

Control flow: compression writes the header, takes a `flate.Writer` from a sync pool, resets it to the output, copies input through it, closes to flush, and returns writer to the pool. Decompression optionally verifies the header, creates a flate reader, and copies decompressed bytes to output.

State and persistence behavior: compressed streams persist the assigned deflate header ID followed by deflate payload. Writer pool state is in-memory only.

Dependencies/integration: registered in the central compression maps and used by content manager compression choices.

Risks and edge cases: decompression does not explicitly close the flate reader, which may be acceptable for this implementation but is worth noting if resource behavior changes. Writer pool reuse depends on `Close` before returning to pool.

Test signals: compressor tests round-trip deflate variants and validate header mismatch rejection.
