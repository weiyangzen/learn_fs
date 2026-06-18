# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage_test.go

## Purpose
Tests coverage file listing and per-file snippet rendering using cached synthetic coverage.

## Important APIs, Types, and Functions
Uses `aflow.NewTestContext`, `aflow.CacheObject`, `symbolizer.Frame`, temporary source files, and `require` assertions.

## Control Flow
`TestCoverageFiles` stores two call-coverage entries and expects sorted unique file paths. `TestFileCoverage` stores line hits for `foo`, writes a source file, invokes `getFileCoverage`, and compares the exact formatted snippet.

## State and Persistence Behavior
Coverage is persisted only in the test context cache; source files live in temp dirs.

## Dependencies and Integration Points
Validates `crash.LoadCoverage` cache contract and `reproduceState.KernelSrc` file lookup.

## Risks and Test Signals
Strong signal for sorting, deduplication, line numbering, and covered-line prefixes. It does not test missing coverage or unsafe filenames.
