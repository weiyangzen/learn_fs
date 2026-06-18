# sources/sync-backup/kopia/repo/compression/compressor_s2.go

Purpose: registers S2 compressor variants, including better compression and parallel writer configurations.

Important APIs/types/functions: constants define parallel concurrency 4 and 8. init registers `s2-default`, `s2-better`, `s2-parallel-4`, and `s2-parallel-8`; `s2Compressor` implements the common compressor interface; `s2DecoderPool` reuses readers.

Control flow: compression writes the Kopia header, resets a pooled `s2.Writer` with configured options, copies input, closes, and returns it. Decompression optionally verifies header, resets a pooled `s2.Reader`, and streams decoded bytes.

State and persistence behavior: output stores a Kopia header followed by S2 stream data. Parallelism affects runtime resources, not file format ID beyond the selected registered header.

Dependencies/integration: registered in global compression maps and used by content manager when selected.

Risks and edge cases: parallel variants can use more goroutines/CPU. Decoder pool reset to nil on return helps avoid retaining input readers.

Test signals: shared compressor tests validate S2 variants round-trip, reject wrong headers, and compress zero data effectively.
