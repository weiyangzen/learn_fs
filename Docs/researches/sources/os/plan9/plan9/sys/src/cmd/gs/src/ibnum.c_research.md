# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.c

Implements Level 2 encoded number reading utilities for PostScript binary object sequences and homogeneous number arrays.

Main functions:
- `num_array_format`: validates encoded number strings or accepts array forms.
- `num_array_size`: computes element count.
- `num_array_get`: retrieves numeric refs from arrays or encoded byte strings.
- `sdecode_number`: decodes 16/32-bit fixed-point integer formats or float formats.
- `sdecodeushort`, `sdecodeshort`, `sdecodelong`, `sdecodefloat`: endian-aware primitive decoders.

Portability details:
- Handles MSB/LSB encoded formats.
- Sign-extends 32-bit longs on platforms where `long` is larger than 4 bytes.
- Converts IEEE floats to native floats if the architecture does not use IEEE native floats.
