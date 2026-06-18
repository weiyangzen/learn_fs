# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.h

Public libbzip2 header.

Defines action constants, return codes, the public `bz_stream` structure, DLL/API macros, and prototypes for:

- `BZ2_bzCompressInit`
- `BZ2_bzCompress`
- `BZ2_bzCompressEnd`
- `BZ2_bzDecompressInit`
- `BZ2_bzDecompress`
- `BZ2_bzDecompressEnd`
- `BZ2_bzBuffToBuffCompress`
- `BZ2_bzBuffToBuffDecompress`
- `BZ2_bzlibVersion`

The header is mostly upstream bzip2 1.0 API surface, with a Plan 9 note that the source was modified and split into smaller pieces.
