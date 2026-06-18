# sources/test-tools/syzkaller/pkg/symbolizer/symbolizer.go

## Purpose

`symbolizer.go` defines the public symbolization types and constructor for the package.

## Important APIs, Types, And Functions

`Frame` describes one symbolized frame with PC, function, file, line, and inline status. `Symbolizer` is an interface with `Symbolize` and `Close`. `Make` returns an `addr2Line` implementation for a `targets.Target`.

## Control Flow, State, Dependencies, And Integration

This file has no persistence and no control flow beyond construction. It decouples callers from the concrete addr2line backend, while the `Frame` struct is shared by cache, addr2line parsing, and tests.

## Risks And Test Signals

The API assumes callers will close symbolizers to avoid subprocess leaks in the concrete implementation. The constructor does not return an error; toolchain lookup errors occur during first symbolization. No direct tests target this thin file, but other symbolizer tests depend on the `Frame` contract.
