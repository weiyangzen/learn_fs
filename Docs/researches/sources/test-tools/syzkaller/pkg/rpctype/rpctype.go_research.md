# sources/test-tools/syzkaller/pkg/rpctype/rpctype.go

## Purpose

`rpctype.go` defines serializable message shapes exchanged over the legacy manager-to-hub `net/rpc` protocol.

## Important APIs, Types, And State

`HubConnectArgs` carries authentication, manager identity, HTTP URL, domain, fresh-corpus flag, supported syscall names, and current corpus. `HubSyncArgs` carries auth identity, repro request flag, corpus additions/removals, and new repros. `HubSyncRes` returns inputs, legacy program list, repros, and a `More` count prompting another sync. `HubInput` adds source domain metadata to a program.

## Dependencies, Integration, Risks, And Test Signals

These are plain exported data structs with no methods or persistence. They integrate with syz-hub RPC server/client code through Go's gob-compatible `net/rpc` encoding. Risks are backward compatibility, especially `HubSyncRes.Progs` retained for legacy managers, and auth material being present in memory/loggable structs. Tests are protocol-level rather than in this file; compile-time field use and hub sync tests are the main signals.
