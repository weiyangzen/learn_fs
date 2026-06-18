# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfparam.c

Parameter read/write support for CCITTFax filters.

It defines the parameter table for shared CCITT fax stream state, including:

- `Uncompressed`, `K`, `EndOfLine`, `EncodedByteAlign`, `Columns`, `Rows`, `EndOfBlock`, `BlackIs1`, `DamagedRowsBeforeError`, `FirstBitLowOrder`, and `DecodedByteAlign`.

Important routines:

- `s_CF_get_params` writes all or non-default parameter values.
- `s_CF_put_params` reads parameters into a copy, validates ranges, and commits on success.

Validation includes limits for `K`, `Columns`, `Rows`, damaged-row tolerance, and `DecodedByteAlign`, with `DecodedByteAlign` required to be a power of two between 1 and 16.

This is image-filter parameter plumbing, not filesystem code.
