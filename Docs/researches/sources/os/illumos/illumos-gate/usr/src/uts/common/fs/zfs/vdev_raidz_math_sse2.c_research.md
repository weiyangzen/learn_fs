# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_sse2.c

This file implements an amd64 SSE2 RAID-Z math backend. It defines a 16-byte aligned `v_t`, XMM register selection macros, and inline assembly helpers for XOR accumulation, register XOR, zeroing, copying, aligned loads, and aligned stores.

GF multiplication by 2 uses SSE2 byte comparison and mask reduction with `0x1d`. General multiplication by an arbitrary coefficient is implemented by generated per-coefficient functions: `mul_x1_*` for one XMM vector and `mul_x2_*` for two vectors. Each function expands `_MUL_PARAM`, repeatedly applying `MUL2` and XORing selected powers of two. Function pointer tables `gf_x1_mul_fns` and `gf_x2_mul_fns` dispatch by coefficient.

The backend wraps vector work in `kfpu_begin()` / `kfpu_end()`, sets wider strides than scalar for bulk operations, includes `vdev_raidz_math_impl.h`, and emits `sse2` generation and reconstruction method tables. The support predicate requires kernel FPU availability plus SSE and SSE2 CPU support.

The exported `vdev_raidz_sse2_impl` registers the implementation with name `"sse2"`. On `__i386`, the file provides only a fakekernel-oriented stub with null method tables.
