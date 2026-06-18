## sources/test-tools/syzkaller/pkg/kfuzztest/description_generation_test.go

Purpose: end-to-end tests for KFuzzTest metadata extraction and syzlang generation from compiled C fixtures.

Important APIs/types/functions: `TestBuildDescriptions`, `runTest`, `flags`, `readTestCases`, and `readTestdata`.

Control flow: discovers testdata subdirectories, skips when the host cannot build Linux/AMD64, compiles `prog.c` with debug info and linker script, calls `ExtractDescription`, compares to `desc.txt`, and removes the built binary.

State and persistence: creates `bin` files under testdata directories during test and removes them.

Dependencies and integration: uses target C compiler, linker script, ELF/DWARF extractor, builder, and expected desc fixtures.

Risks: environment-sensitive due compiler availability. Cleanup uses `rm` command rather than Go removal.

Test signals: strong integration signal for metadata layout, DWARF parsing, annotations, constraints, and syzlang formatting.
