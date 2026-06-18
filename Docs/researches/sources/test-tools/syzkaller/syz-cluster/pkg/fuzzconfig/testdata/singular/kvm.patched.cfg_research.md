# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set kvm.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.
