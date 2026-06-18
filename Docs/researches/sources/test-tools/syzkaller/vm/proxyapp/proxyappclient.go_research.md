# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient.go

## Purpose

`proxyappclient.go` implements the proxyapp VM backend client. It launches or connects to an external JSON-RPC plugin, supervises reconnection, forwards VM pool/instance operations over RPC, streams plugin logs, and adapts run progress into syzkaller output chunks.

## Important APIs, Types, and Functions

Key functions and types include `ctor`, `pool`, `pool.init`, `closeProxy`, `Count`, `Create`, `Close`, `ProxyApp`, `initPipedRPCClient`, `initNetworkRPCClient`, `runProxyApp`, `signalLostConnection`, `ProxyApp.Call`, `doLogPooling`, `CreatePool`, `CreateInstance`, `instance`, `Copy`, `Forward`, `buildMerger`, `Run`, `runStop`, `Diagnose`, `Close`, `stdInOutCloser`, and `clientErrorf`.

## Control Flow

`ctor` parses config, initializes a proxy connection, and starts a supervisor goroutine that reacts to pool close, subprocess termination, lost connection, or retry timers by closing and reinitializing the proxy. `pool.init` either launches a subprocess with piped JSON-RPC or dials TCP/TLS, starts log polling, and calls `ProxyVM.CreatePool`, enforcing a stable pool size. Instance methods translate syzkaller `Copy`, `Forward`, `Run`, `Diagnose`, and `Close` calls to `ProxyVM.*` RPC methods. `Run` starts a remote run, repeatedly issues `RunReadProgress`, writes stdout/stderr/console chunks into an output merger, stops on context cancellation, and emits `SYZFAIL` text on plugin errors.

## State and Persistence Behavior

Pool state includes current proxy pointer, fixed pool count, mutex, close channel, and close result channel. `ProxyApp` stores the RPC client, transfer-content mode, subprocess cancel function, lifecycle channels, and log-polling channels. Transfer-content mode reads image, workdir files, or copied files into RPC request payloads. No durable state is stored locally beyond spawned subprocess lifetime and network connections.

## Dependencies and Integration Points

It depends on `net/rpc/jsonrpc`, TLS/x509, subprocess pipes, `proxyrpc` contracts, syzkaller logging, `vmimpl` interfaces, and `report.Report`. External plugins must implement service name `ProxyVM`.

## Risks and Test Signals

The supervisor must avoid races between close, lost connection, and reinit. Log polling can turn RPC errors into reconnect triggers. File-content transfer may be expensive and uses `WalkDir` path trimming that can produce leading separators. Mutual TLS is unimplemented. Tests cover constructor success/failures, create/copy/forward/diagnose/run RPC behavior, timeout stop, progress errors, TCP/TLS connection setup, lost connection reinit, and subprocess pipe failures.
