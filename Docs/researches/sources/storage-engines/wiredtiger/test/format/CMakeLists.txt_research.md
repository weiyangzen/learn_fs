<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/format/CMakeLists.txt

Purpose: builds the main `test/format` executable `t` and registers its smoke test.

Build contract: `format_sources` lists the full set of C modules implementing format behavior: operations, config, timestamps, replay, backup, compaction, history store, disaggregated support, salvage, verification, and utility modules. `create_test_executable(test_format ... EXECUTABLE_NAME "t" ADDITIONAL_FILES ...)` builds the binary and arranges key config/scripts as additional files. The target uses C++ linker language because sanitizer runtimes and some extension dependencies require C++ linkage. `EXT_LIBPATH` is compiled as an empty string, and `wiredtiger_ext` is an explicit dependency so dlopen-loaded extension modules are built.

State and persistence: declarative CMake; runtime smoke test creates format WT homes through `smoke.sh`.

Dependencies and integration: CTest registers `test_format` as `${CMAKE_CURRENT_BINARY_DIR}/smoke.sh` with `check` label. Depends on repository CMake helper macros and extension target.

Risks and test signals: missing source entries can silently drop format features from the executable. Removing C++ linker selection can break sanitized builds. The extension dependency is needed because runtime loading is invisible to the linker.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/CMakeLists.txt -->
