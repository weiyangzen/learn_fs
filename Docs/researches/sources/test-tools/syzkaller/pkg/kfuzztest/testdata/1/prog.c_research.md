## sources/test-tools/syzkaller/pkg/kfuzztest/testdata/1/prog.c

Purpose: C fixture for KFuzzTest description generation covering a simple pointer-plus-length input struct.

Important APIs/types/functions: `struct pkcs7_parse_message_arg`, `DEFINE_FUZZ_TARGET`, `DEFINE_CONSTRAINT`, `DEFINE_ANNOTATION`, and dummy `main`.

Control flow: compile-time macros place metadata records in custom sections; runtime `main` does nothing.

State and persistence: compiled test binary contains custom sections and DWARF used by Go tests.

Dependencies and integration: includes `common.h`; consumed by `description_generation_test.go`.

Risks: must remain ABI-compatible with extractor record sizes and linker script.

Test signals: verifies array and length annotations plus ignored non-null constraint behavior.
