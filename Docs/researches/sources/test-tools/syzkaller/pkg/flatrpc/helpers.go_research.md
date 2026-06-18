# sources/test-tools/syzkaller/pkg/flatrpc/helpers.go

## Purpose
This file adds Go-side conveniences around generated FlatBuffers object API types. It hides non-idiomatic `RawT` generated names behind stable aliases, provides deep cloning for execution results, translates sandbox names to execution environment flags, and exposes atomic snapshot header state accessors.

## Important APIs, Types, And Functions
`AllFeatures` is a bitmask with every `Feature` bit set. Type aliases such as `ConnectRequest`, `ExecRequest`, `ExecOpts`, `ProgInfo`, and `CallInfo` map generated `*RawT` names to idiomatic package names. `init` verifies that `prog.MaxPids` fits in the `ExecRequest.Avoid` bitset. `(*ProgInfo).Clone` deep-copies `Extra` and per-call `CallInfo` values. `(*CallInfo).clone` clones signal, cover, and comparison slices. `EmptyProgInfo` creates a placeholder result with `ENOSYS` for each call. `SandboxToFlags` maps textual sandbox names to `ExecEnv` bits. `SnapshotHeaderT.UpdateState` and `LoadState` use atomic `uint64` operations through `unsafe.Pointer`.

## Control Flow
Clone logic handles nil receivers, shallow-copies the struct, and then replaces mutable nested slices/pointers with cloned copies. `EmptyProgInfo` appends one failed `CallInfo` per call. `SandboxToFlags` is a simple switch returning either a sandbox enum or a descriptive error.

## State And Persistence Behavior
Cloning is important for queue result deduplication and broadcasting, where one result can be delivered to multiple waiters without sharing mutable slices. Snapshot state is shared-memory-oriented state; atomic store/load prevents torn reads while other fields remain normal generated object fields.

## Dependencies And Integration Points
The file depends on generated `flatrpc` symbols, `prog.MaxPids`, `slices`, `syscall`, and low-level `sync/atomic`/`unsafe`. It is used by fuzzer execution, queue result cloning, manager default exec option setup, and snapshot executor coordination.

## Risks
The `unsafe` atomic conversion assumes `SnapshotState` is represented compatibly with `uint64`. The `init` check guards only PID bitset width, not other wire-size constraints. `AllFeatures = ^Feature(0)` can include unknown future bits; callers must avoid using it as a negotiated capability set without filtering.

## Test Signals
No direct tests are in this item. Indirect signals come from queue clone/dedup behavior, fuzzer execution tests, and any snapshot code that uses atomic state helpers.
