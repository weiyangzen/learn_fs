# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate_test.go

## Purpose
Golden tests for fuzzconfig generation.

## Important APIs, Types, and Functions
TestSingularFocus, TestNoFocus, TestMultipleFocus, runTest, compareOrSave, -write flag.

## Control Flow
Generates base/patched configs and compares normalized JSON against testdata fixtures.

## State and Persistence
Reads fixtures; optional -write rewrites them.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.
