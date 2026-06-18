# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffcompress.c

Split-out libbzip2 buffer-to-buffer compression helper.

Exports `BZ2_bzBuffToBuffCompress()`. It validates parameters, defaults `workFactor` to 30, initializes a `bz_stream`, points it at caller-provided input and output buffers, runs compression with `BZ_FINISH`, updates `*destLen` on success, and maps unfinished output to `BZ_OUTBUFF_FULL`.

This file is marked as modified from upstream mainly to split the library into smaller pieces for the Plan 9 port.
