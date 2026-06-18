# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate.go

## Purpose
Generates syz-manager configs from embedded base/patched templates and api.FuzzConfig focus choices.

## Important APIs, Types, and Functions
GenerateBase, GeneratePatched, applyFuzzConfig, setFocus map, noFlakyFsCalls, noFlakyTraceCalls.

## Control Flow
Loads embedded JSON, merges patched delta when needed, parses mgrconfig partial data, and appends focus-specific syscall/VM adjustments.

## State and Persistence
No persistence; returns in-memory mgrconfig.Config for workflow fuzzing.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.
