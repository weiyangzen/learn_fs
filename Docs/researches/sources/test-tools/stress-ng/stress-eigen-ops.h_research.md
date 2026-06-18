# sources/test-tools/stress-ng/stress-eigen-ops.h

Purpose: declares the C ABI used by `stress-eigen.c` to call Eigen matrix operation implementations compiled from `stress-eigen-ops.cpp`.

Important APIs/types/functions: includes `<stdlib.h>` for `size_t` and declares fifteen functions grouped by operation and scalar type: add, multiply, transpose, inverse, and determinant for long double, double, and float. Every function takes `const size_t size`, `double *duration`, and `double *count`, and returns an int status.

Control flow: none in the header; it defines the contract consumed by the C stressor.

State and persistence behavior: none.

Dependencies and integration points: protected by `STRESS_EIGEN_OPS_H`. It is included inside an `extern "C"` region by the C++ implementation and directly by the C stressor. The return convention is shared: success, failure, or negative library/resource failure.

Risks: prototypes must stay synchronized with the C++ exports and the method table in `stress-eigen.c`. Adding a new operation requires updating all three files coherently.

Test signals: compile/link with `HAVE_EIGEN`; missing or mismatched prototypes surface as compile or link errors. Runtime behavior is tested through `stress-eigen.c`.
