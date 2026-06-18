# sources/test-tools/syzkaller/vm/proxyapp/mocks/subProcessCmd.go

## Purpose

`subProcessCmd.go` is generated testify/mock code for the proxyapp subprocess command abstraction. It lets tests simulate stdin/stdout/stderr pipes, process start, and process wait behavior.

## Important APIs, Types, and Functions

The main type is `mocks.SubProcessCmd` with constructor `NewSubProcessCmd`. It implements `Start`, `StdinPipe`, `StdoutPipe`, `StderrPipe`, and `Wait`, each with typed expectation helper structs.

## Control Flow

Methods call into the embedded mock, return configured values or function-return results, and panic when no return is configured. Cleanup assertions are registered by the constructor.

## State and Persistence Behavior

All state is mock expectation and call history. The mock may hold in-memory pipe objects supplied by tests but creates no external process state itself.

## Dependencies and Integration Points

It depends on `io` and `testify/mock`, and mirrors the `subProcessCmd` interface in `proxyapp/init.go`. It supports tests for `runProxyApp`, pipe initialization failures, subprocess launch, and close behavior.

## Risks and Test Signals

Generated code must be refreshed when `subProcessCmd` changes. Test setup must provide realistic pipe closure behavior to avoid blocked goroutines. Compilation and proxyapp client tests are the main signals.
