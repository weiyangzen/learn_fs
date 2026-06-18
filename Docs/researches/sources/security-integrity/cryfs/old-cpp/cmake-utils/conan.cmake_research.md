# sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake

Purpose: Vendored cmake-conan 0.16.1 helper that bridges CMake configuration to Conan 1.x dependency installation and generated CMake package loading.

Important APIs and types: Key functions/macros include `_get_msvc_ide_version`, `_conan_detect_build_type`, `_conan_check_system_name`, `_conan_check_language`, `_conan_detect_compiler`, `conan_cmake_settings`, `conan_cmake_detect_unix_libcxx`, `conan_cmake_detect_vs_runtime`, `conan_cmake_autodetect`, `conan_cmake_install`, `conan_cmake_run`, `conan_load_buildinfo`, `conan_check`, `conan_add_remote`, and `conan_config_install`.

Control flow: Detection maps CMake compiler/build/os/arch/runtime/libcxx settings into Conan settings. Installation functions parse arguments, construct `conan install` command lines, run Conan in the build directory, and fail or warn based on return code/options. Generated conanfile helpers can write temporary `conanfile.txt`. Loading includes `conanbuildinfo.cmake` or multi-config equivalent and optionally runs `conan_basic_setup`.

State and persistence behavior: Writes generated `conanfile.txt` or temporary copied conanfile markers in the binary dir, runs external Conan commands that populate Conan caches and generated build info, and can add remotes/config to the user Conan configuration.

Dependencies and integration points: Used directly by `DependenciesFromConan.cmake`. It depends on CMake argument parsing, compiler variables, `find_program(conan)`, and Conan CLI version/output formats.

Risks: This is legacy Conan 1.x integration; Conan 2 is not compatible with many options here. Several command builders log full command lines, so env/settings can appear in configure output. Compiler/libcxx autodetection shells out to the compiler preprocessor and can be affected by wrappers/sysroots. Old Visual Studio version mapping stops at VS 2019-era MSVC ranges.

Test signals: Successful configure through `DependenciesFromConan.cmake`, correct dependency target generation, and CI cache reuse are the practical signals. There are no direct unit tests for the vendored helper.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cmake-utils/conan.cmake` completely for this pass (903 lines, 36216 bytes).
