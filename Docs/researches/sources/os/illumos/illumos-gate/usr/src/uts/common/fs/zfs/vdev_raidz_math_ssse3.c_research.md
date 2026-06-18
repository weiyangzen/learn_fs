# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_ssse3.c

This file implements an amd64 SSSE3 RAID-Z math backend. Like the SSE2 backend, it defines a 16-byte vector type and XMM inline assembly macros for load/store/copy/XOR operations, but uses SSSE3 `pshufb` table lookups for faster GF multiplication.

`MUL2` still uses SSE-style mask reduction, while arbitrary coefficient multiplication is handled by `_MULx2()`. That macro splits each byte into high and low nibbles, uses precomputed tables from `gf_clmul_mod_lt[4*256][16]`, applies `pshufb` to produce partial products and reduction terms, and XORs them into the output vectors. This supports two- and four-register multiply cases used by the shared RAID-Z reconstruction template.

The file defines stride and register assignments for all operations expected by `vdev_raidz_math_impl.h`, includes the template, and emits generated method tables for `ssse3`. The exported `vdev_raidz_ssse3_impl` is enabled only when kernel FPU, SSE, SSE2, and SSSE3 are available.

Most of the file is the aligned `gf_clmul_mod_lt` constant table, containing four 16-byte lookup vectors per coefficient. On `__i386`, the file provides only a stub implementation with null method tables and name `"sse3"`.
