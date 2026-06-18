<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh

Purpose: CI smoke script that builds and installs WiredTiger across a matrix of CMake presets and option combinations, then verifies examples and pkg-config output by compiling and running `ex_smoke.c`.

Important functions: argument parsing supports `--generator` and `--parallel`. `discover_compiler()` creates a temporary CMake project with copied `CMakePresets.json` to discover `CMAKE_C_COMPILER` for a preset. `BuildTest(compiler, options, compiler_path)` configures a fresh `build`, builds WiredTiger, builds examples, installs, obtains `pkg-config` flags, compiles `smoke`, and runs it with `LD_LIBRARY_PATH`.

State and persistence: repeatedly deletes and recreates `build`, installs under `installed`, and sets `PKG_CONFIG_PATH`. It leaves the final build/install outputs.

Dependencies and integration: invoked from Evergreen configure-combinations task after `find_cmake.sh` and SWIG setup. Depends on Linux GCC/Clang presets, CMake/Ninja/Make, pkg-config, and examples.

Risks and test signals: the script itself uses `cat >` in the source file, but runtime behavior is intentional. Generator string escaping for Unix Makefiles is delicate. Failures set `ecode=1` after continuing the matrix, providing broad failure coverage but potentially long logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh -->
