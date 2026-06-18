# sources/storage-engines/wiredtiger/test/model/tools/CMakeLists.txt

## Purpose
This CMake file declares the standalone model tools built from `test/model/tools`: the randomized/replay workload runner and the debug-log verifier.

## Important APIs, Types, and Functions
It includes `${CMAKE_SOURCE_DIR}/cmake/helpers.cmake` and uses the project helper `create_test_executable`. Two targets are declared: `model_test` from `model_test/main.cpp`, and `model_verify_debug_log` from `model_verify_debug_log/main.cpp`. Both link `wiredtiger_model` and `wiredtiger_model_test_common`, request C++ compilation with `CXX`, and opt out of `test_util` injection with `NO_TEST_UTIL`.

## Control Flow
CMake evaluation is declarative: include helper functions, then create the two test executables. There are no `add_test` registrations in this file, so these tools may be invoked by scripts, Evergreen tasks, or developers rather than as direct CTest cases from this file.

## State, Persistence, and Integration
The file is an integration bridge between the model library and executable tools. Linking both tools with model and model test common libraries gives them access to workload generation, WiredTiger runner helpers, debug-log parsing, and common verification utilities.

## Risks and Test Signals
Risks are build-level: missing helper definitions, library name changes, or accidentally linking test utility wrappers that conflict with these standalone tools. Successful configuration and compilation are the primary signals. Runtime behavior is covered by the tool sources themselves and by external invocations.
