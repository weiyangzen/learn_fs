# sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml

Purpose: Composite action that configures and builds the legacy CryFS C++ tree with CMake and Ninja for Linux/macOS matrix jobs.

Important APIs and types: Inputs are `cc`, `cxx`, `build_type`, `extra_cmake_flags`, and `extra_cxxflags`. Steps show toolchain versions, run CMake, and run Ninja.

Control flow: The first step prints CMake, Ninja, compiler, and ccache info. The configure step appends extra CXX flags, conditionally adds libc++ debug macros for clang Debug builds, creates `build`, and runs `cmake .. -GNinja` with test builds on, compiler launchers set to ccache, build type, and extra flags. The final step runs `ninja` in `build`.

State and persistence behavior: Creates and populates a `build` directory and ccache artifacts. No source files are modified.

Dependencies and integration points: Called by `main.yaml` Linux and macOS jobs after setup/cache/dependency steps. It expects CMake, Ninja, ccache, and selected compilers to be installed.

Risks: The clang Debug libc++ macros are noted as potentially mismatched on Linux because clang may use libstdc++ instead. The action does not define default values for all inputs, so callers must pass required fields; the macOS caller in `main.yaml` omits extra flag inputs even though the action declares them required, which depends on old GitHub Actions behavior or matrix defaults.

Test signals: Successful CMake configure and Ninja build across compiler/build-type matrix rows are the primary signals. Tool version logging helps diagnose failures.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/.github/workflows/actions/run_build/action.yaml` completely for this pass (56 lines, 1993 bytes).
