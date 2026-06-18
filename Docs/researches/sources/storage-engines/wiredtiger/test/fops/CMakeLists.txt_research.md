<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt

Purpose: builds and registers the `test_fops` file-operation stress executable.

Build contract: `create_test_executable(test_fops SOURCES fops_file.c fops.c t.c)` compiles the three source files into a test binary using the repository's test CMake helper. On Windows, CTest invokes it through `powershell.exe $<TARGET_FILE:test_fops>` because this test has issues running under a normal ctest process, possibly due to resource constraints. Other platforms run `test_fops` directly.

State and persistence: declarative CMake only. Runtime state is created by the executable in its WiredTiger home.

Dependencies and integration: part of the CMake test tree and included in `ctest check`. It depends on shared test utility infrastructure supplied by `create_test_executable`.

Risks and test signals: labels are `check;sanitizer_long`, so it runs in smoke/check lanes and is recognized as long under sanitizers. Changes to source list or invocation affect platform behavior. The Windows special process wrapper is an important integration detail and should not be removed without retesting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt -->
