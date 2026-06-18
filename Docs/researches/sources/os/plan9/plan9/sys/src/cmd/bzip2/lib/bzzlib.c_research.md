# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzzlib.c

Implements the zlib-style convenience API contributed upstream by Yoshioka Tsuneo: `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`.

`bzopen_or_bzdopen` parses mode strings for read/write, compression level, and small decompression mode, opens a path or fd as binary stdio where applicable, then delegates to `BZ2_bzReadOpen` or `BZ2_bzWriteOpen`. Empty or null paths map to stdin/stdout.

The thin `bzread`/`bzwrite` wrappers translate bzip2 errors into `-1`/byte counts. `bzclose` closes the bzip2 wrapper then closes non-stdin/stdout files. `bzerror` maps negative bzip2 error codes to string names.
