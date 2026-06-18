# sources/test-tools/syzkaller/pkg/rpcserver/mocks/Manager.go

## Purpose

This generated file provides a testify/mock implementation of `rpcserver.Manager` for unit tests.

## Important APIs, Types, And Control Flow

`NewManager` binds the mock to a testing object and registers cleanup-time expectation assertions. `Manager` embeds `mock.Mock`; `Manager_Expecter` exposes typed expectation builders. Mocked methods are `BugFrames`, `CoverageFilter`, `MachineChecked`, and `MaxSignal`, each calling `_mock.Called(...)`, supporting direct return values or return functions, and panicking if no return value is configured. Per-method call wrapper types provide `Run`, `Return`, and `RunAndReturn` helpers with typed arguments.

## State, Dependencies, Integration, Risks, And Test Signals

State is the testify mock call registry. Dependencies include `flatrpc`, `queue`, `signal`, `vminfo`, `prog`, and `github.com/stretchr/testify/mock`. It integrates with `rpcserver_test.go` to isolate server behavior from manager state. Risks are typical generated mock risks: stale signatures after interface changes, panics on missing expectations, and unsafe type assertions if test return values are wrong. The file itself is not directly tested; compilation and tests using `mocks.NewManager` are the signal.
