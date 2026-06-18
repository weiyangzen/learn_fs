# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzbuffcompress.c

Duplicate/split variant of the buffer-to-buffer compression helper.

Defines `BZ2_bzBuffToBuffCompress()` with the same behavior as `buffcompress.c`: validate arguments, initialize a compression stream, compress source to destination with `BZ_FINISH`, update destination length, return `BZ_OK`, `BZ_OUTBUFF_FULL`, or the underlying stream error.

The file carries the same Plan 9 note that the upstream libbzip2 source was split into smaller pieces.
