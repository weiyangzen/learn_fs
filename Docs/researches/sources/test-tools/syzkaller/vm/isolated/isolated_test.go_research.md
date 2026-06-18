# sources/test-tools/syzkaller/vm/isolated/isolated_test.go

## Purpose

`isolated_test.go` covers pure helper behavior for the isolated backend: shell quote escaping used for startup scripts and target address parsing.

## Important APIs, Types, and Functions

Tests are `TestEscapeDoubleQuotes` and `TestSplitTargetPort`. They call `vmimpl.EscapeDoubleQuotes` and `splitTargetPort`.

## Control Flow

The escaping test runs a table of strings containing plain text, backslashes, existing escapes, quotes, and a multi-line shell snippet. The split test checks host with explicit port, host with default port, empty target, and malformed port cases.

## State and Persistence Behavior

The tests are pure and create no external state.

## Dependencies and Integration Points

They protect helper behavior used by `isolated.repair` and config validation in `ctor`.

## Risks and Test Signals

They do not cover actual SSH execution, reboot, pstore, or copy/run flows. Strong signals are preserving non-quote escapes, re-escaping double quotes correctly for `bash -c`, defaulting missing port to 22, and rejecting empty targets or invalid ports.
