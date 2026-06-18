# sources/test-tools/syzkaller/pkg/subsystem/service_test.go

## Purpose

This file tests `Service.Children`, confirming that parent-child indexing is built from each subsystem's `Parents` slice.

## Important APIs, Types, And Functions

`TestServiceChildren` creates an unrelated subsystem, a parent, and two children. It constructs a service with `MustMakeService` and asserts that `Children(parent)` returns both children.

## Control Flow, State, Dependencies, And Integration

The test is entirely in-memory and uses pointer identity for the parent key, matching production behavior. It depends on `MakeService` succeeding and on `slices.Clone` not altering expected contents.

## Risks And Test Signals

The test catches regressions where children are not indexed or parent relationships are ignored. It does not test duplicate names, empty names, mutation safety of returned slices, or the nondeterministic `List` method.
