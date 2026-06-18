# sources/test-tools/syzkaller/vm/proxyapp/mocks/ProxyAppInterface.go

## Purpose

`ProxyAppInterface.go` is generated testify/mock code for the proxyapp RPC service interface. It supports unit tests that assert RPC method calls and inject replies/errors.

## Important APIs, Types, and Functions

The main type is `mocks.ProxyAppInterface` with constructor `NewProxyAppInterface`. It implements methods from `proxyrpc.ProxyAppInterface`: `CreatePool`, `CreateInstance`, `Diagnose`, `Copy`, `Forward`, `RunStart`, `RunStop`, `RunReadProgress`, `Close`, and `PoolLogs`, plus typed expectation helper structs.

## Control Flow

Each method delegates to `_mock.Called`, extracts configured return behavior, supports function-valued returns for custom logic, and panics if no return value was specified. The constructor registers cleanup to assert expectations.

## State and Persistence Behavior

State is held in the embedded `mock.Mock`: expected calls, actual calls, and return values. There is no external persistence.

## Dependencies and Integration Points

It depends on `github.com/stretchr/testify/mock` and `vm/proxyapp/proxyrpc` request/reply structs. Tests in the proxyapp package use similar local mocks and can use this generated package for typed expectations.

## Risks and Test Signals

Generated mocks can drift from `proxyrpc.ProxyAppInterface` if not regenerated after interface changes. Because missing returns panic, tests must configure all expected RPC calls. Test signal is successful compilation after RPC interface changes and expectation assertions during unit tests.
