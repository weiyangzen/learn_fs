<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/posixtest_test.go -->
# sources/user-network-fs/go-fuse/posixtest/posixtest_test.go

## Purpose
Runs all registered POSIX conformance tests against either a temp directory or a user-supplied `-posixdir`.

## Important APIs, Types, and Functions
Defines `probeDir` and `TestAll`.

## Control Flow
`TestAll` iterates `All`, skips two known-problem tests, creates a subdirectory per case, and invokes the registered test function.

## State and Persistence Behavior
Test state is per-subtest directory under a temp or supplied root; no persistent repo state is changed.

## Dependencies and Integration Points
Depends on the shared `All` registry in `test.go` and Go's testing flags.

## Risks and Edge Cases
Map iteration order is random, so failures are not ordered. A shared `-posixdir` can retain data between runs if subdirectories are not cleaned externally.

## Test Signals
Running `go test ./posixtest` or embedding the binary in virtiofs QEMU tests exercises the registry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/posixtest_test.go -->
