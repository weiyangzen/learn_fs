# sources/test-tools/syzkaller/pkg/subsystem/entities_test.go

## Purpose

This test file verifies the core mutable graph behavior of `subsystem.Subsystem` from `entities.go`: parent reachability, inherited email expansion, and list filtering. It is important because later Linux subsystem generation and extraction assume parent links are acyclic, inherited mailing lists are safe to use for CC calculation, and filtered subsystem lists do not retain stale parent pointers.

## Important APIs, Types, and Functions

The tests exercise `(*Subsystem).ReachableParents`, `(*Subsystem).Emails`, and `FilterList`. Test fixtures build small in-memory `Subsystem` graphs using `Parents`, `Lists`, `Maintainers`, and `NoIndirectCc`. Assertions use `assert.ElementsMatch` where map iteration or graph traversal order is intentionally unspecified.

## Control Flow

`TestReachableParents` creates a diamond graph and confirms that both direct parents and the shared grandparent are returned once. `TestSubsystemEmails` checks that the current subsystem contributes lists and maintainers, reachable parents contribute only lists, and a parent with `NoIndirectCc` is skipped for inherited CC. `TestFilterList` removes one parent from a list and confirms both the returned list and the surviving entity's `Parents` field are updated.

## State, Dependencies, Risks, and Test Signals

The tests mutate heap-allocated `Subsystem` objects directly and rely on pointer identity. There is no persistence or I/O. Dependencies are the local `subsystem` package and `github.com/stretchr/testify/assert`. Main risks covered are duplicate traversal through shared ancestors, leaking maintainers from parents, ignoring `NoIndirectCc`, and retaining filtered-out parents. They do not cover cycle panic behavior or email deduplication, which means those remain residual risks for callers.
