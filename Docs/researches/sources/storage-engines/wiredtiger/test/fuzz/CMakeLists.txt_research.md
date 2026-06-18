# sources/storage-engines/wiredtiger/test/fuzz/CMakeLists.txt

Purpose: CMake build/test definition for WiredTiger libFuzzer targets.

Important APIs and functions: `check_c_source_compiles` detects clang libFuzzer support; `add_library(fuzz_util SHARED fuzz_util.c)` builds the fuzz utility library; `create_test_executable` builds `test_fuzz_modify` and `test_fuzz_config`; `add_test` runs each target through `fuzz_run.sh`.

Control flow: it temporarily sets CMake required flags/libraries for fuzzer detection, returns early if libFuzzer is missing, selects `wiredtiger_static` when static+PIC is enabled or `wiredtiger_shared` when shared is enabled, returns early otherwise, builds `fuzz_util` with include paths and sanitizer flags, then defines and registers fuzz executables.

State and persistence: affects build graph only. It copies `fuzz_run.sh` as an additional file for each target and links sanitizer runtime into fuzz targets.

Dependencies and integration: depends on CMake helper macros from the WiredTiger build, `test_util`, configured include directories, clang `-fsanitize=fuzzer`, and either shared or PIC static WiredTiger library.

Risks and test signals: targets silently skip when prerequisites are unavailable, with a status message for library shape but not for missing fuzzer. Link/compile failures usually indicate sanitizer/toolchain mismatch or missing PIC/shared library support.
