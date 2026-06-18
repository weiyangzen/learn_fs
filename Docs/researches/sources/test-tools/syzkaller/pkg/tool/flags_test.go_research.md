# sources/test-tools/syzkaller/pkg/tool/flags_test.go

## Purpose

This file unit-tests command flag parsing helpers, arch-list validation, `CfgsFlag`, and optional-flag escaping.

## Important APIs, Types, And Functions

`TestParseFlags` covers normal flags, unknown hard flags, and ignored unknown optional flags. `TestCfgsFlagString`, `TestCfgsFlagSet`, and `TestCfgsFlagAlreadySet` validate `CfgsFlag`. `TestParseArchList` checks bad OS, bad arch, all Linux arches, and selected arches. `TestFlagEscapeUnescape` checks normal, space, special, control, empty, truncated, and invalid hex cases.

## Control Flow, State, Dependencies, And Integration

Tests allocate fresh flag sets and discard parser output. They depend on current `targets.List` contents for Linux arch expectations. Assertions use testify `assert` and `require`.

## Risks And Test Signals

These tests catch command-line compatibility regressions. The Linux arch list is intentionally exact, so target additions/removals require test updates. The tests do not cover repeated `ParseFlags` calls on one flag set or empty comma values in `CfgsFlag.Set`.
