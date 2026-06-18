# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_scalar.c

This file provides the portable scalar RAID-Z math backend. It selects a native 32-bit or 64-bit integer lane size, wraps it in `v_t`, and defines the template macros from `vdev_raidz_math_impl.h` in terms of ordinary loads, stores, XORs, and byte-wise table multiplication.

`raidz_init_scalar()` fills `vdev_raidz_mul_lt[256][256]`, a direct GF multiplication lookup table. Reconstruction multiplication uses this table by coefficient, avoiding repeated log/exp operations during recovery. `MUL2` is optimized with word-wide bit masks for carry reduction by the RAID-Z polynomial, and `MUL4` applies `MUL2` twice.

The scalar backend defines one-lane strides for all zero/copy/add/syndrome/reconstruction operations, includes the shared template, and emits scalar generation and reconstruction method arrays with `DEFINE_GEN_METHODS(scalar)` and `DEFINE_REC_METHODS(scalar)`.

`raidz_will_scalar_work()` always returns true, making this the fallback implementation. The exported `vdev_raidz_scalar_impl` supplies `.init = raidz_init_scalar`, the generated method tables, the support predicate, and name `"scalar"`. The file also defines the public aligned `vdev_raidz_pow2` and `vdev_raidz_log2` GF tables used by broader RAID-Z math code.
