# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzread.c

Implements the lower-level stdio decompression API: `BZ2_bzReadOpen`, `BZ2_bzRead`, `BZ2_bzReadClose`, and `BZ2_bzReadGetUnused`.

`BZ2_bzReadOpen` validates parameters, copies any caller-supplied unused compressed bytes into the `bzFile` buffer, initializes `bz_stream`, then calls `BZ2_bzDecompressInit`. `BZ2_bzRead` fills `avail_out`, refills compressed input with `fread` when needed, repeatedly calls `BZ2_bzDecompress`, handles stream end, I/O errors, and unexpected EOF.

`BZ2_bzReadClose` ends decompression and frees the wrapper. `BZ2_bzReadGetUnused` is only valid after `BZ_STREAM_END` and returns remaining compressed bytes in the decompressor input buffer.
