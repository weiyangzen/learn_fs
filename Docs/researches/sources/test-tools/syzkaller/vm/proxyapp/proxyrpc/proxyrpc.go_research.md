# sources/test-tools/syzkaller/vm/proxyapp/proxyrpc/proxyrpc.go

## Purpose

`proxyrpc.go` defines the JSON-RPC service contract between syzkaller's proxyapp VM backend and external proxy VM plugins.

## Important APIs, Types, and Functions

The main interface is `ProxyAppInterface` with methods `CreatePool`, `CreateInstance`, `Diagnose`, `Copy`, `Forward`, `RunStart`, `RunStop`, `RunReadProgress`, `Close`, and `PoolLogs`. Request/reply structs include `CreatePoolParams/Result`, `CreateInstanceParams/Result`, `CopyParams/Result`, `ForwardParams/Result`, `RunStartParams/Reply`, `RunStopParams/Reply`, `RunReadProgressParams/Reply`, `CloseParams/Reply`, `DiagnoseParams/Reply`, and `PoolLogsParam/Reply`.

## Control Flow

There is no executable control flow. The client calls these methods under service name `ProxyVM`; plugins implement the interface and fill reply structs. Run execution is split into start, progress polling, stop, and close operations.

## State and Persistence Behavior

The structs carry state across RPC boundaries: pool config, image/workdir/file byte payloads, instance IDs, run IDs, output chunks, errors, finish flags, and log messages. Persistence is plugin-defined.

## Dependencies and Integration Points

It is imported by the proxyapp client, tests, generated mocks, and external plugin implementations. It intentionally carries simple JSON-serializable fields.

## Risks and Test Signals

Interface changes are wire-contract changes for plugins and require mock regeneration. Large byte fields can be expensive when transfer-content mode is enabled. Tests should verify backward-compatible plugin behavior, run progress sequencing, error propagation, and pool log verbosity handling.
