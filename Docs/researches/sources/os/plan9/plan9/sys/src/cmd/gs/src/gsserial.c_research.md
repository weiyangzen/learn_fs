# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.c

## Purpose
Implements variable-length little-endian integer serialization utilities used for compact command-list/object encodings.

## Public Surface
- `enc_u_size_uint(uint uval)`: returns byte count for unsigned base-128 encoding.
- `enc_s_size_int(int ival)`: returns byte count for signed encoding, handling minimum integer specially.
- `enc_u_put_uint(uint uval, byte *ptr)`: writes unsigned encoding and returns pointer after it.
- `enc_s_put_int(int ival, byte *ptr)`: writes signed encoding and returns pointer after it.
- `enc_u_get_uint(uint *pval, const byte *ptr)` / `enc_u_get_uint_nc(...)`: decode unsigned from const or non-const byte pointers.
- `enc_s_get_int(int *pval, const byte *ptr)` / `enc_s_get_int_nc(...)`: decode signed from const or non-const byte pointers.

## Encoding Model
- Unsigned values are base-128 little-endian digits with high bit `0x80` as continuation.
- Signed values use bit `0x40` in the first byte as the sign bit and reserve the high bit for continuation.
- Signed minimum integer cannot be negated normally, so size and encode/decode logic treat it as a special boundary case.

## Unit Test Block
Under `UNIT_TEST`, the file contains round-trip tests around powers of two for unsigned and signed values, checking encoded length and decoded equality for const and non-const decoding APIs.

## Dependencies
Includes `stdpre.h`, `gstypes.h`, and `gsserial.h`. Most fast paths are macro-defined in the header; this file supplies fallback/large-value routines.

## Risks and Notes
- Decode routines trust that the input buffer contains a terminating byte; malformed unbounded input could overrun the available buffer because no length parameter is accepted.
- Signed encoding depends on two's-complement-like boundary assumptions embodied by `enc_s_min_int`.
