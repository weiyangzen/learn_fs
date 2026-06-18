# sources/test-tools/stress-ng/stress-matrix-3d.c

Purpose: implements `matrix-3d`, a CPU/FP/cache/memory stressor for cubic `N x N x N` float matrices. It stresses access-order effects and arithmetic kernels in both x-y-z and z-y-x traversal orders.

Important APIs/types/functions: `stress_matrix_3d_type_t` is `float`; `stress_matrix_3d_func_t` uses VLA arguments. Kernel pairs implement add, sub, trans, scalar mult/div, Hadamard, Frobenius, copy, mean, zero, negate, and identity. `matrix_3d_methods[]` maps names to xyz/zyx functions and includes `all`. `stress_matrix_3d_exercise()` allocates matrices, initializes data, times kernels, optionally verifies by recomputation, and emits metrics.

Control flow: `stress_matrix_3d()` catches SIGILL, reads method/order/size options, page-rounds memory size, reports memory use, synchronizes, and calls the exercise helper. The helper maps `a`, `b`, `r`, and optional `s`; hints collapse; initializes random data; repeatedly invokes the selected kernel; advances `method_all_index` for `all`; and unmaps in reverse allocation order.

State and persistence: static state tracks the current method and `all` index; metrics are reset each run. All matrix storage is anonymous mmap and is not persistent.

Dependencies/integration: requires compiler support for VLA function arguments and excludes PCC. Uses target clones, unroll pragmas, mmap/madvise helpers, SIGILL catch, method options, memory accounting, and optional verification.

Risks/test signals: cubic memory growth is large. Useful signals are method enumeration, successful allocation or resource failure, optional verification without `memcmp` differences, per-method `matrix-3d ops per sec` metrics, and unimplemented path on unsupported compilers.
