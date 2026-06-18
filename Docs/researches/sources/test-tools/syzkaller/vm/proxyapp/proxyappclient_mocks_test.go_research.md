# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_mocks_test.go

## Purpose

`proxyappclient_mocks_test.go` contains test-local mock and fixture support for proxyapp client tests.

## Important APIs, Types, and Functions

The file defines helper mock command runner/process fixtures used by `proxyappclient_test.go`, including mock command runner setup, subprocess pipe behavior, and server fixture initialization around `proxyrpc.ProxyAppInterface`.

## Control Flow

Fixtures create in-memory pipes, a JSON-RPC server registered as `ProxyVM`, a fake subprocess command exposing those pipes, and default mock expectations for `CreatePool` and log polling. Tests customize returned errors or RPC replies per scenario.

## State and Persistence Behavior

All state is in memory: pipes, mock expectations, channels for wait/log notifications, and RPC server goroutines. No filesystem or network state is required for piped-mode tests.

## Dependencies and Integration Points

It depends on `net/rpc/jsonrpc`, `io.Pipe`, `testify/mock`, `proxyrpc`, and proxyapp's `subProcessCmd` abstraction. It is a support layer rather than production code.

## Risks and Test Signals

Fixture correctness is important because dead pipes or missing expectations can hang tests. The main signal is the broader proxyapp client test suite passing without leaked goroutines or unmet mock expectations.
