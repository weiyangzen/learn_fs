# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.c

Sample unpacking entry module. It defines endian-dependent lookup tables for 1-bit expansion and instantiates unpacking templates for shared-map and interleaved multi-map cases.

Key behavior:
- Builds `lookup4x1to32_identity` and `lookup4x1to32_inverted` differently for big-endian and little-endian CPUs.
- Handles compiler constant quirks for 32-bit and 64-bit long expressions.
- `sample_unpack_copy` returns the original data pointer when no unpacking/copying is needed and updates `pdata_x`.
- Includes `gxsamplp.h` twice:
  - once for single lookup map functions `sample_unpack_1/2/4/8`,
  - once for interleaved component maps `sample_unpack_1/2/4/8_interleaved`.

Notable dependencies:
- `gxsample.h` for public declarations and sample lookup types.
- `gximage.h` and `gxfixed.h` for image context.
- Template implementation in `gxsamplp.h`.

Research notes:
- The lookup tables are deliberately typed as aligned integer arrays rather than byte arrays.
- This module is compile-time template instantiation rather than hand-written separate functions.
