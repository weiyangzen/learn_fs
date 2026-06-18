# sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems_test.go

## Purpose

This test file validates the end-to-end Linux subsystem generation pipeline with a synthetic MAINTAINERS file and in-memory source tree.

## Important APIs, Types, and Functions

Tests call `listFromRepoInner`, `prepareTestLinuxRepo`, `ensureParents`, `subsystem.MakePathMatcher`, and use `testRules`. The embedded `testMaintainers` fixture covers VFS, ext4, freevxfs, memory management, tmpfs, UDF, and THE REST.

## Control Flow

`TestGroupLinuxSubsystems` verifies list-based grouping, name derivation, and maintainer selection after path rules are ignored for comparison. `TestCustomCallRules` adds an extra UDF subsystem and syscall rules, then verifies syscall attachment and improved VFS maintainer selection after UDF is excluded from list grouping. `TestLinuxSubsystemPaths` builds a matcher from generated subsystems and checks expected subsystem names for representative paths. `TestLinuxSubsystemParents` verifies inferred parent links and then a custom parent override.

## State, Dependencies, Risks, and Test Signals

All repository state is modeled through `fstest.MapFS`; subsystem objects are mutated by the pipeline. Dependencies are `io/fs`, `testing`, `testing/fstest`, `subsystem`, and `testify/assert`. The tests give high-value integration coverage for generation behavior without a real kernel checkout. They do not cover production `linuxSubsystemRules`, dangling-rule failures, debug info contents, sorting stability directly, or error paths such as missing `MAINTAINERS`.
