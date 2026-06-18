## sources/test-tools/syzkaller/pkg/kfuzztest/testdata/common.h

Purpose: test-only C definitions mirroring kernel KFuzzTest metadata section records.

Important APIs/types/functions: `struct kfuzztest_target`, `struct kfuzztest_constraint`, `struct kfuzztest_annotation`, enums for constraints/annotations, and macros `DEFINE_FUZZ_TARGET`, `DEFINE_CONSTRAINT`, `DEFINE_ANNOTATION`.

Control flow: macros declare static objects in named custom sections and mark them used; they also keep input struct definitions alive.

State and persistence: object files contain aligned metadata records read by Go extractor tests.

Dependencies and integration: must match Go sizes in `types.go` and linker script start/end symbols.

Risks: alignment/field layout mismatch with Go parser breaks tests. Comments contain typos but do not affect behavior.

Test signals: foundational fixture for all KFuzzTest description generation tests.
