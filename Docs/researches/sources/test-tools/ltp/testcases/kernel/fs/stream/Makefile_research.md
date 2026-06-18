# sources/test-tools/ltp/testcases/kernel/fs/stream/Makefile

Purpose: LTP leaf Makefile for stdio stream behavior tests. It sets `top_srcdir`, includes the standard `testcases.mk`, and then `generic_leaf_target.mk`; no test-specific libraries or flags are added. The file integrates the five `stream0*.c` test programs into the LTP build system. State is build-only, with runtime tmpdir requirements declared in each C file. Risks are limited to LTP make include path correctness. Test signal is successful discovery and compilation of the stream testcase binaries.
