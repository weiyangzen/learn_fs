# sources/test-tools/stress-ng/stress-eigen.c

Purpose: implements the C-side `eigen` stressor that selects Eigen matrix methods, controls matrix size, runs operations via the C++ bridge, records per-method metrics, and registers stress-ng options.

Important APIs/types/functions: `stress_eigen_func_t` is the common function pointer type for bridge calls. `stress_eigen_method_info_t` maps method names to functions. `eigen_methods[]` contains `all` plus all scalar/operation combinations. `stress_eigen_method()` exposes method names to option parsing. `stress_eigen_all()` rotates through concrete methods for the `all` pseudo-method. `stress_eigen_exercise()` runs the selected method loop, handles return codes, emits per-method metrics, and computes a geometric mean debug rate. `stress_eigen()` handles settings and lifecycle.

Control flow: the stressor reads `--eigen-method` and `--eigen-size` with minimize/maximize bounds, synchronizes start, and calls `stress_eigen_exercise()`. The exercise loop calls the selected function until stop. When method zero is selected, `method_all_index` advances across concrete methods each iteration. After the loop, metrics are emitted for methods that recorded duration.

State and persistence behavior: `current_method`, `method_all_index`, and static `eigen_metrics[]` are process-local runtime state. No filesystem state is created. Matrix allocation and verification live in the C++ file.

Dependencies and integration points: requires `HAVE_EIGEN`; otherwise registers as unimplemented with reason `eigen C++ library, headers or g++ compiler not used`. Uses stress-ng option parsing, process state, metrics, and math `frexp/pow`. Registered as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE`, `VERIFY_ALWAYS`.

Risks: method table order must match the `all` rotation assumption that concrete methods start at index 1. Large sizes up to 1024 can be very costly, especially inverse and determinant. Return `-1` from the C++ bridge is treated as resource/library skip; `EXIT_FAILURE` is a verification failure.

Test signals: run `--eigen-method all` and each named method at small sizes, run maximize/minimize size modes, confirm per-method metrics include matrix size, and build without Eigen to validate unimplemented registration.
