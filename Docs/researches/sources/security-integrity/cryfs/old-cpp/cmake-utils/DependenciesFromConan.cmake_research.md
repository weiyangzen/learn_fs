# sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake

Purpose: Default dependency configuration for the legacy C++ build that resolves range-v3, spdlog, and Boost through Conan.

Important APIs and types: Includes `cmake-utils/conan.cmake`, calls `conan_cmake_autodetect(settings)`, `conan_cmake_install(PATH_OR_REFERENCE ... BUILD missing SETTINGS ${settings})`, includes `${CMAKE_BINARY_DIR}/conanbuildinfo.cmake`, and calls `conan_basic_setup(TARGETS SKIP_STD NO_OUTPUT_DIRS)`. It defines interface targets `CryfsDependencies_range-v3`, `CryfsDependencies_spdlog`, and `CryfsDependencies_boost`.

Control flow: On configure, CMake autodetects Conan settings, installs missing dependencies from `conanfile.py`, imports generated build info, and maps Conan package targets to CryFS-specific dependency targets.

State and persistence behavior: Conan downloads/builds dependency packages into the configured Conan cache and writes generated CMake files into the build tree.

Dependencies and integration points: Included by the main CMake configuration when no custom `DEPENDENCY_CONFIG` is specified. The CryFS targets link against the `CryfsDependencies_*` interface targets instead of direct Conan targets.

Risks: This relies on Conan 1.x behavior and generated `CONAN_PKG::*` targets. `BUILD missing` can compile dependencies during configure, making configure slower and dependent on remote availability. ABI/compiler setting autodetection must match the selected CMake compiler.

Test signals: Successful CMake configure and later linking against range-v3, spdlog, and Boost consumers prove this file works.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/DependenciesFromConan.cmake` completely for this pass (19 lines, 675 bytes).
