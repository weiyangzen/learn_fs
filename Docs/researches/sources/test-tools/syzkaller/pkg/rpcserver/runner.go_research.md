# sources/test-tools/syzkaller/pkg/rpcserver/runner.go

## Purpose

`runner.go` represents one connected executor runner. It performs the executor handshake, streams execution requests, receives execution/status messages, updates queues and stats, canonicalizes coverage, tracks last executing programs, and handles shutdown.

## Important APIs, Types, And Functions

`Runner` holds identity, queue distributor, proc count, coverage/filter/debug flags, sys target, stats, connection, request/executing/hanged maps, `LastExecuting`, VM status callbacks, machine info, and result channel. `handshakeConfig` and `handshakeResult` carry setup options, files, features, coverage filter, and canonicalizer. Core methods are `Handshake`, `ConnectionLoop`, `sendRequest`, `handleExecutingMessage`, `handleExecResult`, `convertCallInfo`, `SendSignalUpdate`, `SendCorpusTriaged`, `Stop`, `Shutdown`, `MachineInfo`, `QueryStatus`, and `Alive`.

## Control Flow

`Handshake` sends `ConnectReply`, receives `InfoRequest`, invokes the server callback, sends `InfoReply`, and stores connection/machine/canonicalizer state. `ConnectionLoop` marks the VM executing, services pending status requests, fills the executor queue up to `2 * procs`, receives executor messages, and dispatches executing, exec-result, or state-result handling. `sendRequest` serializes syz programs, binaries, or glob requests into `flatrpc.ExecRequest`, sets return flags, avoid masks, and debug env flags, and records the request by ID. `handleExecResult` normalizes call counts, converts coverage/signal/comparisons, merges extra coverage, adds fallback signal if coverage is disabled, reports success/failure/hang, and completes the queue request.

## State, Dependencies, Integration, And Risks

Mutable request state is mostly touched by the connection goroutine, while `mu` protects connection, stop, and machine info. Dependencies include `flatrpc`, `queue`, `cover`, `stat`, `osutil`, `report`, `prog`, `targets`, and dispatcher status hooks. Integration points are executor FlatBuffers protocol, queue scheduling, VM crash context, coverage canonicalization/filtering, and manager signal distribution. Risks include blocked sends to a dead executor, malformed proc/request IDs, program serialization failures, stale hanged request results, bad coverage poisoning corpus signal, and shutdown needing to finish outstanding requests exactly once.

## Test Signals

Runner behavior is exercised indirectly by `rpcserver_test.go` and the `runtest` executor/local RPC tests, especially coverage/comparison canonicalization, status handling, restarts, and queue completion paths.
