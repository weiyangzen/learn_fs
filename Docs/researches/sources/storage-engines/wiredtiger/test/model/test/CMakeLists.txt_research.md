# sources/storage-engines/wiredtiger/test/model/test/CMakeLists.txt

Purpose: defines the CMake build wiring for model tests and shared test utilities.

Important APIs and targets: includes `cmake/helpers.cmake`; creates shared library `wiredtiger_model_test_common` from `common/subprocess.cpp`, `common/util.cpp`, and `common/wiredtiger_util.cpp`; sets public include directory `common/include`; sets private include directories for WT source include, test utility, and generated config; links `wiredtiger_model`, `wt::wiredtiger`, and `test_util`; creates test executables `test_model_basic`, `test_model_checkpoint`, `test_model_rts`, `test_model_transaction`, and `test_model_workload`; adds copy command/target for `test_model.sh`.

Control flow: common library is built first and linked into each test executable. The custom command copies the shell test script into the binary tree, and `wiredtiger_model_test_common` depends on that copy target.

State and persistence: no runtime model state. Build output is the shared utility library, test binaries, and copied script in the build directory.

Dependencies and integration: depends on project-level helper macros, WT targets, `wiredtiger_model`, and `test_util`. The `CXX NO_TEST_UTIL` options signal C++ test executables without default test utility wiring beyond explicit libs.

Risks: adding a new common source or test executable requires this file. The copy target dependency names `test_model.sh` as output/dep target and may need care if script location changes. Include directory visibility controls whether tests can include common headers.

Test signals: successful configuration/build should produce all five model test executables and the common shared library. CTest/script integration depends on copied `test_model.sh`.
