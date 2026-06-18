# sources/test-tools/syzkaller/pkg/subsystem/linux/parents_test.go

## Purpose

This test file validates the hierarchy-transformation heuristics used after Linux subsystem records are matched against a repository tree.

## Important APIs, Types, and Functions

Tests call `MakeCoincidenceMatrix`, `dropSmallSubsystems`, `dropDuplicateSubsystems`, `transitiveReduction`, `BuildCoincidenceMatrix`, and `setParents`. They use synthetic `subsystem.Subsystem` instances with path rules and `testing/fstest.MapFS` to avoid real kernel checkout dependencies.

## Control Flow

`TestDropSmallSubsystems` records enough files for kernel/net/fs but not legal and checks the small subsystem is removed. `TestDropDuplicateSubsystems` covers exact overlap with alphabetical-list preference, acceptable 66% overlap, and a high-overlap child that is dropped. `TestTransitiveReduction` starts with redundant ancestor links and confirms only direct edges remain. `TestSetParents` builds path matches for kernel, net, wireless, and drivers, then verifies inferred parent edges.

## State, Dependencies, Risks, and Test Signals

State is in-memory and graph mutations happen on test objects. Dependencies are `testing`, `testing/fstest`, `subsystem`, and `testify/assert`. These tests give strong signals for intended heuristics but do not cover loop creation failures, existing parent links before inference, syscall-retained small subsystems, exact threshold boundaries, nil path rules, or nondeterministic callback ordering.
