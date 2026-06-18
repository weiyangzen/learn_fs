# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_impl.h

This header is the shared RAID-Z math implementation template. It is included by scalar and SIMD-specific `.c` files after they define the vector type, load/store/XOR/multiply macros, stride constants, and `raidz_math_begin/end` hooks. The same algorithmic code is therefore compiled into multiple implementations.

It computes reconstruction coefficients for Q, R, PQ, PR, QR, and PQR recovery with Galois-field helpers such as `gf_exp2`, `gf_exp4`, `gf_mul`, `gf_div`, and `gf_inv`. It also provides common ABD iteration callbacks for zeroing, copying, XOR addition, and multiplication by a constant.

Parity generation covers RAIDZ1 P, RAIDZ2 PQ, and RAIDZ3 PQR. P parity is simple XOR accumulation, while Q and R syndromes repeatedly multiply prior syndrome state by 2 or 4 in the RAID-Z GF(2^8) field before adding data. The generator functions operate over ABD-backed columns and handle shorter data columns by continuing syndrome updates through the parity column length.

Reconstruction covers one-, two-, and three-data-column loss using P/Q/R combinations. The code first builds syndromes by treating missing data as zero, adds stored parity columns, then transforms syndromes with precomputed coefficients to recover targets. For uneven RAID-Z geometry, shorter target columns may be temporarily replaced with full-size ABD buffers so vector loops can avoid per-iteration size branches, then copied back.

Key entry points emitted through this template are the `raidz_generate_*_impl()` and `raidz_reconstruct_*_impl()` routines consumed by `DEFINE_GEN_METHODS()` and `DEFINE_REC_METHODS()` in the concrete implementation files. The main dependencies are `raidz_map_t`, ABD iteration helpers, RAID-Z column constants, and the implementation-provided vector macros.
