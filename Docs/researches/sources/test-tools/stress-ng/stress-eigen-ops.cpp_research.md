# sources/test-tools/stress-ng/stress-eigen-ops.cpp

Purpose: provides the C-callable C++ Eigen operation implementations used by the `eigen` stressor: matrix addition, multiplication, transpose, inverse, and determinant across `long double`, `double`, and `float`.

Important APIs/types/functions: templated helpers `eigen_add<T>`, `eigen_multiply<T>`, `eigen_transpose<T>`, `eigen_inverse<T>`, and `eigen_determinant<T>` allocate random dynamic Eigen matrices, time an operation, repeat it, and verify the result against `THRESHOLD`. The `extern "C"` block exports fifteen functions declared in the header, such as `eigen_add_double()` and `eigen_determinant_float()`.

Control flow: each exported function simply instantiates the matching template. Each template catches all C++ exceptions and returns `-1` for library/resource failure, `EXIT_FAILURE` for verification mismatch, or `EXIT_SUCCESS`. Durations and operation counts are accumulated through caller-provided pointers for stress-ng metrics.

State and persistence behavior: all matrices are stack/local Eigen objects with heap storage owned by Eigen and freed by normal C++ destruction. No static mutable state and no filesystem state are used.

Dependencies and integration points: compiled only when `HAVE_EIGEN` is defined. Includes `config.h`, `stress-eigen-ops.h`, and `<eigen3/Eigen/Dense>`, and imports C `stress_time_now()`. The C ABI avoids C++ name mangling for calls from `stress-eigen.c`.

Risks: large matrix sizes can cause allocation failures or expensive inverses/determinants. Exact repeatability depends on Eigen deterministic operations over identical inputs; threshold comparisons handle normal FP error. Catch-all exception handling maps failures to skip/resource behavior in the C wrapper.

Test signals: build with and without Eigen/g++; run each `--eigen-method`, check duration/count increments, verify failures are reported for mismatches, and confirm C/C++ linkage produces all expected symbols.
