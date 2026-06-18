## sources/test-tools/syzkaller/pkg/kfuzztest/testdata/2/prog.c

Purpose: richer C fixture for KFuzzTest extraction with nested struct pointer, strings, arrays, length annotation, and multiple constraints.

Important APIs/types/functions: `struct bar`, `struct foo`, `DEFINE_FUZZ_TARGET`, several `DEFINE_CONSTRAINT` and `DEFINE_ANNOTATION` calls, and dummy `main`.

Control flow: macros emit target/constraint/annotation metadata at compile time; extractor later follows DWARF nested struct references.

State and persistence: compiled test binary stores metadata and debug info.

Dependencies and integration: includes `common.h`; used by description generation tests.

Risks: comments mention `foo.bar` while field is `b`, but macro uses `bar`, which can intentionally/accidentally refer to a non-existent field depending expected output. Fixture depends on compiler DWARF stability.

Test signals: exercises string/array/len annotations and nested struct emission.
