<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt

Purpose: Builds the `catch2-unittests` executable and registers it as the `unittest` CTest target.

Important APIs/types/functions: Defines `unittests` differently for assertion-overriding builds versus normal builds; includes block, cross-checkpoint-cache, cursor, extension, sub-level-error, truncate, live-restore, wrapper, and utility sources. Uses `create_test_executable`, links `Catch2::Catch2`, conditionally defines `KEY_PROVIDER_EXTENSION`, and adds POSIX dependency `wiredtiger_dir_store`.

Control flow: CMake branches on `HAVE_UNITTEST_ASSERTS` and `WT_WIN`, then composes `unittest_sources`.

State and persistence behavior: Build-only state; generated executable runs tests under CTest label `check;unittest`.

Dependencies and integration points: Pulls in shared helpers like `block/util_block.cpp` and all files in this work item; integrated by parent `test/CMakeLists.txt`.

Risks and test signals: Source-list drift is easy when adding tests. The signal is successful configure/build plus `ctest -R unittest` or direct `catch2-unittests [tag]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/CMakeLists.txt -->
