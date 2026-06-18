# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.h

Defines encoded-number constants and decoder declarations.

Key points:
- Enables `BYTE_SWAP_IEEE_NATIVE_REALS` to emulate an Adobe interpreter byte-swapping bug for native IEEE reals.
- Defines encoded number array marker byte `149`.
- Defines PostScript number formats for int32, int16, IEEE/native float, and byte-order bits.
- Provides validity and byte-count helpers, including `num_array` as a special format for ordinary arrays.
- Declares format detection, size, element extraction, and low-level numeric decoders.

Research notes:
- Constants match PostScript Language Reference binary object formats.
- The header separates external format policy from decoder implementation.
