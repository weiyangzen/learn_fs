# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzwrite.c

Implements lower-level stdio compression APIs: `BZ2_bzWriteOpen`, `BZ2_bzWrite`, `BZ2_bzWriteClose`, and `BZ2_bzWriteClose64`.

`BZ2_bzWriteOpen` validates stream, block size, verbosity, and work factor, then initializes `BZ2_bzCompressInit`. `BZ2_bzWrite` feeds caller input to `BZ2_bzCompress(BZ_RUN)`, flushing produced bytes through `fwrite` from the internal buffer.

Close paths optionally abandon, otherwise finish the stream with repeated `BZ2_bzCompress(BZ_FINISH)` calls, write remaining compressed bytes, `fflush`, return 32/64-bit byte counters from `bz_stream`, end compression, and free the wrapper.
