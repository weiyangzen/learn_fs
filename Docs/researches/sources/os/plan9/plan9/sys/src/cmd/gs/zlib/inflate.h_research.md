# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.h

## Purpose
Internal header defining inflate modes and the persistent `inflate_state` structure.

## Key Definitions
Enables gzip decoding by defining `GUNZIP` unless `NO_GZIP` is set.

Defines `inflate_mode`, including:
- Header modes: `HEAD`, gzip-specific `FLAGS`, `TIME`, `OS`, `EXLEN`, `EXTRA`, `NAME`, `COMMENT`, `HCRC`.
- Dictionary modes: `DICTID`, `DICT`.
- Block modes: `TYPE`, `TYPEDO`, `STORED`, `COPY`, `TABLE`, `LENLENS`, `CODELENS`.
- Decode modes: `LEN`, `LENEXT`, `DIST`, `DISTEXT`, `MATCH`, `LIT`.
- Trailer/done/error modes: `CHECK`, gzip `LENGTH`, `DONE`, `BAD`, `MEM`, `SYNC`.

## `inflate_state`
Stores:
- Current mode and wrapper flags.
- Checksum and total output counters.
- Sliding window fields.
- Bit accumulator fields.
- Current copy length, match offset, and extra-bit count.
- Active literal/length and distance decode tables.
- Dynamic table-building arrays: `lens[320]`, `work[288]`, and `codes[ENOUGH]`.

## Usage
Included by `inflate.c`, `infback.c`, and `inffast.c`. It is an internal ABI and is explicitly not intended for application use.
