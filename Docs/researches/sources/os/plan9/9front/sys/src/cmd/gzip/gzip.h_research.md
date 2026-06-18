# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.h

Defines gzip header constants used by `gzip.c` and `gunzip.c`.

Key points:
- Defines gzip magic bytes `0x1f`, `0x8b`.
- Defines compression method `GZDEFLATE`.
- Defines gzip header flag bits:
  - `GZFTEXT`
  - `GZFHCRC`
  - `GZFEXTRA`
  - `GZFNAME`
  - `GZFCOMMENT`
  - `GZFMASK`
- Defines extra flag values `GZXFAST` and `GZXBEST`.
- Defines gzip OS identifiers from FAT through Acorn RISCOS and unknown.
- Defines CRC polynomial `GZCRCPOLY`.
- Maps Plan 9/Inferno output OS code to Unix via `GZOSINFERNO = GZOSUNIX`.

Dependencies and interactions:
- Shared by gzip compressor and decompressor.
- Constants match RFC 1952 gzip framing.

Research relevance:
- Small format contract header for the native gzip tools.
