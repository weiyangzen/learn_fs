# sources/test-tools/stress-ng/stress-matrix.c

Purpose: implements `matrix`, a 2D CPU/FP/cache/memory stressor for `N x N` float matrices. It exercises arithmetic kernels and contrasts x-y versus y-x traversal for cache behavior.

Important APIs/types/functions: `stress_matrix_type_t` is `float`; `stress_matrix_func_t` uses VLA matrix parameters. Kernels include product, add, sub, transpose, scalar multiply/divide, Hadamard, Frobenius, copy, mean, zero, negate, identity, and square. `matrix_methods[]` maps method names to xy/yx implementations. `stress_matrix_exercise()` performs mapping, initialization, kernel timing, optional shadow verification, metric emission, and cleanup.

Control flow: `stress_matrix()` catches SIGILL, reads `matrix-method`, `matrix-yx`, and `matrix-size`, page-rounds storage, reports memory for `a`, `b`, and `r`, synchronizes, and calls the exercise helper. The helper allocates matrices, initializes random scaled values, repeatedly executes the chosen kernel, optionally recomputes into `s` and compares, rotates through concrete methods for `all`, then emits rates and a debug geometric mean.

State and persistence: only static method/metric state persists within the process. Matrix memory is anonymous and fully unmapped on exit.

Dependencies/integration: requires VLA argument support and uses target clones, unroll pragmas, math `frexp`/`pow`, mmap/madvise helpers, method options, memory accounting, metrics, and optional verification.

Risks/test signals: large sizes can exhaust memory, especially with verification’s fourth matrix. Deterministic `memcmp` verification assumes identical operations on the same inputs. Useful signals are method selection, memory-use report, no verification differences, per-method metrics, and unimplemented registration when VLA arguments are unavailable.
