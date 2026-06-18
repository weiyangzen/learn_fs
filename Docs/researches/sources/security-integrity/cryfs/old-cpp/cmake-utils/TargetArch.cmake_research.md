# sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake

Purpose: Provides a vendored `target_architecture(output_var)` function that detects the target CPU architecture at CMake configure time, including cross-compile scenarios where the generated program cannot be run.

Important APIs and types: The central data is `archdetect_c_code`, a C preprocessor probe that emits `#error cmake_ARCH <arch>`. The public function handles `CMAKE_OSX_ARCHITECTURES` specially on Apple and otherwise writes `arch.c`, enables C, runs `try_run`, and parses compile output.

Control flow: Apple multi-arch settings are normalized and validated manually. Non-Apple detection compiles a deliberately failing C source, captures compiler output, extracts the architecture token with a regex, and falls back to `unknown` if parsing fails.

State and persistence behavior: Writes `${CMAKE_BINARY_DIR}/arch.c` during configure. There is no runtime persistence.

Dependencies and integration points: Included by `cmake-utils/utils.cmake`, which exposes `get_target_architecture`. It supports packaging/build logic that needs architecture names.

Risks: The file is old vendored code and recognizes a limited set of architectures. `try_run` is used for compile-output capture despite no real execution being needed. Apple PowerPC support is disabled unless `ppc_support` is set. Unknown newer architectures become `unknown` and may break downstream packaging.

Test signals: There are no local tests. Configure messages or consumers of `get_target_architecture` are the functional signal.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/TargetArch.cmake` completely for this pass (145 lines, 6990 bytes).
