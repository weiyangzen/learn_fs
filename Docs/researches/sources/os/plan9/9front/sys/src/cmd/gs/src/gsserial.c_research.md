# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.c

Implements utility routines for compact variable-length integer serialization.

Key behavior:
- `enc_u_size_uint` and `enc_s_size_int` compute encoded sizes for unsigned and signed integers.
- `enc_u_put_uint` and `enc_s_put_int` write little-endian base-128 encodings with a continuation bit.
- `enc_u_get_uint`, `enc_u_get_uint_nc`, `enc_s_get_int`, and `enc_s_get_int_nc` decode const and non-const byte-pointer streams.
- Signed encoding stores sign in the next-to-high bit of the first byte and handles `enc_s_min_int` specially.
- A `UNIT_TEST` block round-trips unsigned and signed values around powers of two and checks encoded lengths.

Dependencies:
- Uses `gstypes.h` and constants/macros from `gsserial.h`.

Research notes:
- This is a low-level format helper originally split out from command-list code.
- The non-const wrappers delegate to the const decoders and advance by pointer difference.
