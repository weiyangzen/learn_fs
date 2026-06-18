# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.c

Implements Level 2 encoded-number array/string decoding.

Key behavior:
- Defines `enc_num_bytes` table from header constants.
- `num_array_format` validates encoded number strings or recognizes regular arrays/packed arrays.
- Encoded number strings must start with byte value 149, contain a valid format byte, and have a count matching payload length.
- `num_array_size` returns element count for encoded strings or ordinary arrays.
- `num_array_get` reads from either a normal array or encoded number string; only integer/real array elements are accepted.
- `sdecode_number` decodes fixed-point 16/32-bit integers or real floats according to format and binary scale.
- Short/ushort/long decoders honor big/little endian format bits.
- `sdecodefloat` handles native floats directly or converts IEEE float bits on non-IEEE platforms.

Research notes:
- It emulates Adobe behavior for binary object sequences through format handling in the companion header.
- The array path and encoded-string path converge on returning integer/real refs or errors.
