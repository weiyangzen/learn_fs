# sources/storage-engines/foundationdb/contrib/stacktrace/CMakeLists.txt

Purpose: This CMake file builds the local stacktrace contribution as a static library from `stacktrace.amalgamation.cpp`, publishes the `include` directory, disables clang-tidy for this target, and wires sanitizer-specific compile definitions into the stacktrace implementation.

Important APIs, types, and functions: The build target is `stacktrace`. `add_library(stacktrace STATIC stacktrace.amalgamation.cpp)` creates the archive. `target_include_directories(stacktrace PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")` exposes headers such as `stacktrace/stacktrace.h` to downstream targets. Sanitizer options map `USE_ASAN` to `ADDRESS_SANITIZER`, `USE_MSAN` to `MEMORY_SANITIZER`, `USE_UBSAN` to `UNDEFINED_BEHAVIOR_SANITIZER`, and `USE_TSAN` to both `THREAD_SANITIZER` and `DYNAMIC_ANNOTATIONS_EXTERNAL_IMPL=1`.

Control flow: During CMake configure/generate, the file declares the static library and target properties. At compile time, exactly one sanitizer branch in the `if/elseif` chain contributes private definitions if the corresponding cache variable is enabled. Consumers link against `stacktrace` and inherit only the public include path, not the sanitizer defines.

State and persistence behavior: The file does not own runtime state or persistence. It controls how the stacktrace runtime is compiled. Sanitizer definitions can change code paths inside the amalgamated implementation, especially for signal-safety, unwind behavior, or annotations.

Dependencies and integration points: It depends on the source file `stacktrace.amalgamation.cpp` and the public include tree under `include`. It integrates with the repository's top-level sanitizer variables and any target linking to the static `stacktrace` library. The empty `CXX_CLANG_TIDY` target property opts the vendored/amalgamated code out of clang-tidy checks.

Risks: Sanitizer selection is mutually exclusive because of `elseif`; if multiple `USE_*SAN` variables are set, only the first in ASAN, MSAN, UBSAN, TSAN order applies. Private sanitizer definitions mean consumers do not see matching preprocessor flags unless supplied elsewhere. Disabling clang-tidy can hide modernization or warning issues in the amalgamation, though it is likely intentional for third-party code. If `stacktrace.amalgamation.cpp` is missing or the include path layout changes, the target breaks at configure/build time.

Test signals: Configure and build the target in normal, ASAN, MSAN, UBSAN, and TSAN builds; confirm `stacktrace/stacktrace.h` is reachable from a dependent target; inspect compile commands for the expected sanitizer definition; ensure clang-tidy is not run on this target; and run a small executable that links `stacktrace` and captures a stack trace in each supported build mode.
