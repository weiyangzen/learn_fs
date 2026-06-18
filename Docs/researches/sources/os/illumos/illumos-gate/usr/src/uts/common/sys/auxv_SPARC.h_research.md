# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_SPARC.h

This header defines SPARC-specific hardware capability bit values for auxiliary vector reporting.

Key contents:
- `AV_SPARC_*` bits for legacy arithmetic capability, V8+/VIS/VIS2/VIS3, block init ASIs, FMA variants, HPC, random, transactions, crypto/hash instructions, Montgomery/multiple-precision multiply, CRC32C, pause, compare-and-branch, and cache sparing.
- `FMT_AV_SPARC` bit-format string.
- Obsolete compatibility aliases:
  - `AV_SPARC_HWMUL_32x32`
  - `AV_SPARC_HWDIV_32x32`
  - `AV_SPARC_HWFSMULD`

Dependencies:
- Intended to be included by `sys/auxv.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is an ABI support header for hardware capability consumers.
- Several values are explicitly legacy or obsolete aliases.
