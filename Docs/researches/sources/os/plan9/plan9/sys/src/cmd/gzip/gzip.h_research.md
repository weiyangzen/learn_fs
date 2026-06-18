# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.h

Shared gzip-format constants for `gzip.c` and `gunzip.c`.

- Defines gzip magic bytes, deflate method ID, header flag bits, extra flag meanings, OS identifiers, and CRC polynomial.
- Sets `GZOSINFERNO` to `GZOSUNIX`, so this implementation writes Unix-style OS code.
- Provides no functions or state.

This header is a compact local protocol definition for gzip member parsing and generation.
