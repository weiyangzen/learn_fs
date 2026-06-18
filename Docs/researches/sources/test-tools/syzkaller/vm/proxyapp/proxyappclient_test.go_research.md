# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_test.go

## Purpose

`proxyappclient_test.go` is the main unit suite for piped proxyapp client behavior. It verifies constructor failures, pool creation, close behavior, and instance method RPC translations.

## Important APIs, Types, and Functions

Tests cover `ctor`, `pool.Create`, `pool.Close`, `instance.Close`, `Diagnose`, `Copy`, `Forward`, and `Run`. Helpers include `makeTestParams`, `makeMockProxyAppProcess`, `poolFixture`, `proxyAppServerFixture`, `createInstanceFixture`, and `contextWithTimeout`.

## Control Flow

Fixtures run an in-memory JSON-RPC server over pipes exposed by a mocked subprocess command. Tests set mock expectations for RPC calls, invoke the proxyapp pool or instance methods, and assert return values, errors, output chunks, and timeout behavior. Run tests simulate `RunStart`, repeated `RunReadProgress`, plugin errors, RPC errors, finished replies, and cancellation.

## State and Persistence Behavior

The tests use in-memory pipes, goroutines, mock state, and contexts. They do not launch real subprocesses or VMs.

## Dependencies and Integration Points

They exercise piped JSON-RPC setup, log polling, pool-size enforcement, instance ID propagation, error-to-output conversion through `clientErrorf`, and `vmimpl.ErrTimeout` behavior.

## Risks and Test Signals

Some TODOs remain for periodic subprocess crash handling and pool close plugin API behavior. Strong signals include constructor errors for bad config or broken pipes, create failures surfacing, copy/forward/diagnose RPC mapping, run timeout calling `RunStop`, plugin progress errors producing `SYZFAIL`, and finished progress returning nil error.
