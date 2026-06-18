# sources/test-tools/syzkaller/pkg/subsystem/lists/linux_test.go

## Purpose

This test file regression-tests the registered Linux subsystem list through the public subsystem extractor. It protects expected routing from crash evidence, especially cases where a generic guilty path should be overridden or supplemented by syzkaller reproducer calls.

## Important APIs, Types, And Functions

`TestLinuxUpstreamSubsystems` obtains `subsystem.GetList("linux")`, builds `subsystem.MakeExtractor`, and runs table-driven cases with `[]*subsystem.Crash`. Inputs combine `GuiltyPath` and `SyzRepro`; expected results are subsystem names such as `xfs`, `ntfs3`, `dri`, `usb`, `wireless`, and `v9fs`.

## Control Flow, State, Dependencies, And Integration

Each case calls `group.Extract`, collects subsystem names, and compares with `assert.ElementsMatch`. The test depends on package registration from the generated/static Linux list and the extractor behavior in `pkg/subsystem`. There is no persistence; all state is test-local. Integration coverage is high because it exercises real Linux rules, path matching, syscall extraction from repro programs, voting behavior, and parent removal through the public API.

## Risks And Test Signals

The file is sensitive to Linux list drift: a legitimate subsystem-rule update may require expected-output changes. It intentionally checks ambiguous evidence, stale names such as old NTFS routing to `ntfs3`, broad `mm`/`arm` paths, and overlapping USB/media evidence. Failures here signal user-visible syzbot CC/routing regressions rather than isolated parser problems.
