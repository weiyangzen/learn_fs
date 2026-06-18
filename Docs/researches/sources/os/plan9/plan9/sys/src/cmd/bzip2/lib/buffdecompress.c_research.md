# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffdecompress.c

Split-out libbzip2 buffer-to-buffer decompression helper.

Exports `BZ2_bzBuffToBuffDecompress()`. It validates pointers, `small`, and verbosity, initializes decompression, points the stream at caller-provided buffers, runs one decompression call, updates `*destLen` on stream end, and distinguishes output-buffer exhaustion from unexpected EOF when decompression returns `BZ_OK`.

Like the other split files, it is upstream libbzip2 code reorganized for the Plan 9 tree.
