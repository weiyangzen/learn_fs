# sources/test-tools/syzkaller/pkg/signal/signal_test.go

## Purpose

This test validates priority-aware signal intersection.

## Important APIs, Types, And Flow

`TestIntersectsWith` constructs a base signal from raw elements `0..4` at priority 1. It asserts intersection with an overlapping signal at the same priority, no intersection with disjoint elements, and no intersection when the other signal overlaps but has lower priority.

## State, Dependencies, Risks, And Test Signals

The test uses `testify/assert` and deterministic raw input. It does not cover `Merge`, `DiffRaw`, `Intersection`, `Minimize`, or raw ordering. Its signal is focused but important: priority is part of intersection, not only element membership.
