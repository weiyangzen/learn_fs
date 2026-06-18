# Research: sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt

## sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt

Purpose: Build and test-variant definition for the `test_checkpoint` executable.

Important declarations: `create_test_executable(test_checkpoint)` compiles `checkpointer.c`, `workers.c`, and `test_checkpoint.c`, and includes `recovery-test.sh` as an additional file. The target linker language is forced to CXX for sanitizer and extension runtime compatibility.

Control flow/integration: `define_test_variants` registers many named variants covering mixed tables, row store, variable-length column store, named checkpoints, prepare, timestamps, sweep stress, long-running SERVER-93028 cases, and disaggregated leader/PALite cases with precise checkpoint. Labels include `check`, `test_checkpoint`, `long_running`, and `check_disagg`.

State and persistence: build metadata only. Runtime persistence is controlled by the executable variants' flags.

Dependencies/integration: depends on WiredTiger test CMake helper macros and extension availability for disaggregated/PALite variants. Risks include variant flag drift from executable option parsing, long-running cache-size tuning, and forced C++ linkage assumptions. Test signals are CTest variant registrations and successful executable builds/runs.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/CMakeLists.txt -->
