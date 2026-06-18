# sources/test-tools/syzkaller/pkg/flatrpc/flatrpc.go

## Purpose

`flatrpc.go` is generated Go code from `pkg/flatrpc/flatrpc.fbs`. It is the FlatBuffers wire-contract binding for syzkaller's lightweight RPC protocol between the host-side manager/runner code and target-side executors, plus the shared-memory snapshot protocol used by QEMU snapshot execution. The file defines enum constants, raw FlatBuffers table/struct readers, object-API `*RawT` structs, packing/unpacking helpers, root-buffer constructors, mutation helpers, and vector builders.

The file itself contains no business logic beyond generated serialization mechanics. Its value is that it freezes binary layout and field order for messages shared across Go, generated C++ headers, executor code, RPC server code, VM snapshot code, and tests.

## Important APIs, Types, And Functions

Top-level enum families:

- `Const` defines cross-language size constants: `MaxInputSize`, `MaxOutputSize`, `SnapshotShmemSize`, and `SnapshotDoorbellSize`.
- `Feature` is a bitmask of kernel/executor capabilities such as coverage, comparisons, sandbox modes, fault/leak support, network setup, USB/VHCI/Wi-Fi emulation, swap, and memory dump.
- `HostMessagesRaw` and `ExecutorMessagesRaw` are FlatBuffers union discriminants for host-to-executor and executor-to-host envelopes.
- `RequestType`, `RequestFlag`, `ExecEnv`, `ExecFlag`, `CallFlag`, and `SnapshotState` encode execution mode, requested result data, executor environment, per-run collection behavior, per-call outcome flags, and snapshot synchronization state.

Each enum has generated `EnumNames*`, `EnumValues*`, and `String()` methods. Callers use these maps for diagnostics, feature iteration, and tests, but unknown bit combinations stringify as `Type(number)` rather than decomposing bitmasks.

Generated message families:

- Connection handshake: `ConnectHelloRawT`, `ConnectRequestRawT`, `ConnectReplyRawT`.
- Machine info exchange: `InfoRequestRawT`, `InfoReplyRawT`, `FileInfoRawT`, `GlobInfoRawT`, `FeatureInfoRawT`.
- Envelope messages: `HostMessageRawT` wraps `ExecRequestRaw`, `SignalUpdateRaw`, `CorpusTriagedRaw`, or `StateRequestRaw`; `ExecutorMessageRawT` wraps `ExecResultRaw`, `ExecutingMessageRaw`, or `StateResultRaw`.
- Execution request/result: `ExecOptsRawT`, `ExecRequestRawT`, `SignalUpdateRawT`, `CorpusTriagedRawT`, `StateRequestRawT`, `ExecutingMessageRawT`, `CallInfoRawT`, `ComparisonRawT`, `ProgInfoRawT`, `ExecResultRawT`, `StateResultRawT`.
- Snapshot protocol: `SnapshotHeaderT`, `SnapshotHandshakeT`, `SnapshotRequestT`.

Generated function patterns repeat for most tables:

- `Pack(builder)` serializes an object-API `*RawT` value into a `flatbuffers.Builder`.
- `UnPackTo(t)` and `UnPack()` materialize object-API values from raw FlatBuffers readers.
- `GetRootAs<Type>`, `GetSizePrefixedRootAs<Type>`, `Finish<Type>Buffer`, and `FinishSizePrefixed<Type>Buffer` attach the generated reader to root buffers.
- `Init`, `Table`, field accessors, `Mutate*` methods, `<Type>Start`, `<Type>Add<Field>`, vector start helpers, and `<Type>End` implement the low-level generated FlatBuffers API.

Struct-backed FlatBuffers types differ from table-backed types:

- `ExecOptsRaw` is a fixed 24-byte struct containing `env_flags`, `exec_flags`, and `sandbox_arg`; it is inserted with `PrependStructSlot`.
- `ComparisonRaw` is a fixed 32-byte struct containing `pc`, `op1`, `op2`, and `is_const`; vectors of comparisons use 32-byte elements.

## Control Flow

Serialization is builder-driven and proceeds bottom-up:

1. A caller creates an object-API value such as `ExecRequestRawT` or `ExecutorMessageRawT`.
2. `Pack` recursively serializes nested strings, byte vectors, scalar vectors, table vectors, and structs first.
3. The generated `<Type>Start`/`Add`/`End` functions write the parent table into the FlatBuffers builder.
4. Companion `conn.go` calls `builder.FinishSizePrefixed(off)` when sending over TCP.

Deserialization is table-driven:

1. `GetRootAs<Type>` or companion `Parse` initializes a raw generated table over a byte slice.
2. Raw accessors read fields lazily from the underlying buffer and return default zero values when fields are absent.
3. `UnPack()` eagerly copies the raw table into object-API Go structs, recursively allocating slices for vectors and nested tables.
4. Union envelopes first read `MsgType`, then initialize the matching raw table and unpack to the typed `Value` inside `HostMessagesRawT` or `ExecutorMessagesRawT`.

Important protocol flows represented by this file:

- RPC connection setup starts with `ConnectHelloRaw`, proceeds through `ConnectRequestRaw`, and returns `ConnectReplyRaw` with run parameters, feature setup requests, leak/race frame filters, and files to read from the VM.
- Machine checking uses `InfoRequestRaw` to return feature and file statuses and `InfoReplyRaw` to send coverage filters back.
- Host execution dispatch sends `HostMessageRaw` containing `ExecRequestRaw`, `SignalUpdateRaw`, `CorpusTriagedRaw`, or `StateRequestRaw`.
- Executor responses arrive as `ExecutorMessageRaw` containing a fast crash-leading `ExecutingMessageRaw`, a full `ExecResultRaw`, or a `StateResultRaw`.
- Snapshot mode uses `SnapshotHeader`, `SnapshotHandshake`, and `SnapshotRequest` in shared memory rather than the TCP envelope path.

## State And Persistence Behavior

This file does not own durable persistence, files, sockets, goroutines, or long-lived mutable service state. State exists in three transient forms:

- Builder state while packing messages; the companion connection layer resets the builder after each send.
- Byte-slice-backed raw tables while receiving; raw readers alias the receive buffer and are only valid while that buffer remains unchanged.
- Object-API unpacked structs; these allocate independent Go slices for many scalar/table vectors, but byte-vector accessors such as `DataBytes`, `OutputBytes`, `ProgDataBytes`, and `StateResultRaw.DataBytes` return slices backed by the FlatBuffers buffer.

Mutation helpers such as `MutateId`, `MutateFlags`, `MutateOutput`, and `MutateState` mutate fields in the backing FlatBuffers byte slice. They are useful for controlled in-place edits but are unsafe as a general persistence model because callers must ensure the backing buffer is valid, mutable, and not shared in conflicting ways.

The snapshot types model state shared with non-Go code. `SnapshotHeaderT` is later extended in `helpers.go` with atomic `UpdateState` and `LoadState`; this matters because snapshot synchronization crosses host/target/shared-memory boundaries.

## Dependencies

Direct dependencies in this file are minimal:

- `github.com/google/flatbuffers/go` provides `Builder`, `Table`, `Struct`, scalar readers/writers, vector access, buffer roots, and size-prefixed framing helpers.
- `strconv` is used only by enum `String()` fallbacks.

Practical dependencies are broader:

- `flatrpc.fbs` is the authoritative schema source; edits should be made there and regenerated rather than editing this generated Go file.
- `flatrpc.h` is the corresponding generated C++ binding consumed by executor-side code.
- `helpers.go` aliases generated `*RawT` names to idiomatic names like `ExecRequest`, `ProgInfo`, `CallInfo`, and `ExecOpts`, and adds package helpers such as `AllFeatures`, `SandboxToFlags`, cloning, and snapshot atomic state helpers.
- `conn.go` provides TCP framing, generic `Send`, generic `Recv`, parsing, and corruption checks around these raw generated types.

## Integration Points

Primary Go integrations include:

- `pkg/rpcserver/rpcserver.go` and `pkg/rpcserver/runner.go`, which use `Connect*`, `Info*`, `HostMessage`, `ExecutorMessage`, and typed execution result messages for fuzzer/manager communication.
- `pkg/runtest`, `pkg/vminfo`, `pkg/ifaceprobe`, `tools/syz-execprog`, `syz-manager`, and `syz-verifier`, which build `ExecRequest`, inspect `ProgInfo`/`CallInfo`, evaluate `Feature` bitmasks, and convert sandbox/coverage choices into `ExecEnv` and `ExecFlag`.
- `syz-manager/snapshot.go` and `vm/qemu/snapshot_linux.go`, which use `SnapshotHandshakeT`, `SnapshotRequestT`, `SnapshotHeaderT`, and the shared size constants for snapshot execution over shared memory.
- Executor C++ code through the generated `flatrpc.h` and comments in `flatrpc.fbs`, especially `ExecEnv`, whose changes must stay aligned with executor-side flag parsing.

The generated API is also part of the repo's public-ish internal contract: many call sites import `pkg/flatrpc` aliases from `helpers.go`, but those aliases resolve directly to the `*RawT` object API types defined here.

## Risks And Edge Cases

- This is generated code. Manual edits will be overwritten and can desynchronize Go from the schema and C++ generated header.
- Several generated `Pack` methods assume nested pointers are non-nil. For example, `HostMessageRawT.Pack` calls `t.Msg.Pack`, `ExecRequestRawT.Pack` calls `t.ExecOpts.Pack`, `ProgInfoRawT.Pack` calls `t.Extra.Pack`, and `ExecResultRawT.Pack` calls `t.Info.Pack` without first checking those fields. Callers must populate required nested object fields or avoid packing incomplete objects.
- Several generated `UnPackTo` methods assume nested raw fields exist before calling `.UnPack()` on them. Malformed or partial buffers can panic unless protected by the companion parsing layer.
- Raw accessors and byte-vector methods alias backing buffers. Code that stores returned slices after another receive on the same connection can observe overwritten data unless it copies.
- `UnPack()` allocates slices based on vector lengths from the buffer. Companion `conn.go` explicitly verifies executor messages before unpacking to prevent corrupted lengths from causing unbounded allocation.
- Enum values are numeric wire contracts. Reordering or changing existing values would break compatibility with executors and saved/intermediate binary messages.
- Bitmask enum `String()` methods do not render combined flags. Diagnostics for combined `Feature`, `ExecEnv`, `ExecFlag`, and `CallFlag` values need explicit bit iteration if human-readable decomposition matters.
- Snapshot constants and layout offsets are coupled to shared memory mapping in VM code; changing `ConstMaxInputSize`, `ConstMaxOutputSize`, or `ConstSnapshotShmemSize` affects mmap sizing and offset calculations.

## Test Signals

Useful existing test coverage is mostly around consumers rather than this generated file directly:

- `pkg/flatrpc/conn_test.go` exercises connection framing, send/receive behavior, and parsing safeguards around generated messages.
- `pkg/rpcserver/rpcserver_test.go` uses `ConnectHello`, `ConnectRequest`, `ConnectReply`, feature masks, and local `flatrpc.Conn` instances to validate handshake behavior.
- `pkg/runtest/run_test.go` and `pkg/runtest/executor_test.go` validate execution flags, call result flags, coverage, comparisons, and program info expectations built from these types.
- `pkg/vminfo/*_test.go` checks feature and syscall discovery using `FeatureInfo`, `FileInfo`, `ExecRequest`, and `ProgInfo`.
- Snapshot users in `syz-manager/snapshot.go` and `vm/qemu/snapshot_linux.go` provide compile-time signals that the generated snapshot layouts and constants still match host-side expectations.

A strong regression check after schema changes is to regenerate `flatrpc.go` and `flatrpc.h`, then run package tests for `pkg/flatrpc`, `pkg/rpcserver`, `pkg/runtest`, `pkg/vminfo`, and any executor/snapshot build targets that consume the generated C++ header.
