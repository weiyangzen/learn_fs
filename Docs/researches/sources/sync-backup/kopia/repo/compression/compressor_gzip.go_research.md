# sources/sync-backup/kopia/repo/compression/compressor_gzip.go

Purpose: registers gzip compressor variants using the standard `compress/gzip` package.

Important APIs/types/functions: init registers `gzip`, `gzip-best-speed`, and `gzip-best-compression`; `gzipCompressor` has header ID, header bytes, and a writer pool; `gzipDecoderPool` reuses decoder objects.

Control flow: `Compress` writes the Kopia compression header, takes/resets a gzip writer, streams input, closes to finish the gzip trailer, and returns it to the pool. `Decompress` optionally verifies the header, takes a pooled reader, resets it on input, copies to output, and returns it.

State and persistence behavior: output stores a Kopia header followed by gzip stream bytes. Pools are process-local and reduce allocations.

Dependencies/integration: registered in global compression registry and used by content formatting when selected.

Risks and edge cases: `mustSucceed(dec.Reset(input))` will panic on malformed gzip setup errors; later stream corruption is returned by copy errors. Pool correctness depends on reset/close sequencing.

Test signals: compressor tests validate gzip round trips, wrong-header failures, and basic compression ratio expectations.
