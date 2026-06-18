# sources/test-tools/syzkaller/pkg/tool/tool.go

## Purpose

`tool.go` provides common command-line tool initialization, HTTP serving, and fatal-exit helpers.

## Important APIs, Types, And Functions

`Init` registers profiling flags, parses command-line flags through `ParseFlags`, and returns the profiling cleanup function. `ServeHTTP` listens on a TCP4 address and serves the default HTTP mux in a goroutine. `Failf` prints to stderr and exits with status 1; `Fail` formats an error through `Failf`.

## Control Flow, State, Dependencies, And Integration

`Init` mutates the global `flag.CommandLine` and process profiling state. `ServeHTTP` logs fatal errors and exits the process on listen or serve failure. This package is integrated by syzkaller command binaries that want consistent optional-flag and profiling behavior.

## Risks And Test Signals

The comment misspells `ServeHTTP` as `ServeHTPP`. Because helpers exit the process on errors, direct unit testing is limited. Risks include global flag registration conflicts and ungraceful HTTP server termination. `flags_test.go` covers the parsing layer used by `Init`.
