# sources/test-tools/syzkaller/pkg/cover/backend/dwarf_test.go

Purpose: unit-tests high-risk helpers in the DWARF backend: GCC KCOV precision gating, Android source path normalization, and architecture-specific call target decoding.

Important APIs/types/functions: `TestIsKcovBrokenInCompiler`, `TestCleanPathAndroid`, `TestNextCallTargetARM64`, and `TestNextCallTargetAMD64`. Test helper structs `CleanPathAndroidTest` and `NextCallTargetTest` model expected path triples and decoded call targets.

Control flow: compiler-version tests feed representative GCC, g++, clang, and malformed strings into `isKcovBrokenInCompiler`. Android path tests vary delimiters, absolute paths, cache paths, and existence predicates. Call-target tests construct raw instruction byte sequences and pass them to `nextCallTarget` with `arches["arm64"]` or `arches["amd64"]`.

State and persistence: no persistent state; tests use in-memory slices and fake existence functions.

Dependencies and integration: imports only `testing`, but depends on unexported backend internals in the same package. It complements higher-level `report_test.go` by covering deterministic helpers without compiling binaries.

Risks: call-target coverage excludes s390x despite production support. Android path tests use synthetic existence callbacks, so filesystem edge cases remain covered only indirectly. Version parsing expectations encode the current policy that unparseable GCC-like strings are unsafe.

Test signals: failures directly indicate broken callback scanning or path normalization, both of which can cause false callback mismatch errors or missing source files in reports.
