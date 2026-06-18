# sources/test-tools/syzkaller/pkg/flatrpc/flatrpc.h

## Purpose
This is an automatically generated C++ FlatBuffers header for the `rpc` protocol used between syzkaller host-side code and executor-side code. It defines the serialized schema for connection handshakes, feature negotiation, execution requests and results, corpus/state sideband messages, and snapshot-mode shared-memory coordination. It is intentionally generated and should be changed by editing the FlatBuffers schema and regenerating rather than by hand.

## Important APIs, Types, And Functions
The header requires FlatBuffers 23.5.26 by static assertion and wraps all generated types in namespace `rpc`. It declares constants in `Const`, including snapshot doorbell size, maximum input/output sizes, and snapshot shared-memory size. Feature negotiation uses the `Feature` bitmask enum, covering coverage, comparisons, sandbox modes, fault/leak detection, network/device emulation, KCSAN, swap, and memory dump capabilities.

Host-to-executor traffic is modeled by `HostMessageRaw` carrying a `HostMessagesRawUnion`. The union can hold `ExecRequestRaw`, `SignalUpdateRaw`, `CorpusTriagedRaw`, or `StateRequestRaw`, with `As*` accessors, `Set`, `Reset`, `Pack`, and `UnPack`. Executor-to-host traffic is symmetric via `ExecutorMessageRaw` and `ExecutorMessagesRawUnion`, carrying `ExecResultRaw`, `ExecutingMessageRaw`, or `StateResultRaw`.

Execution-specific enums include `RequestType` (`Program`, `Binary`, `Glob`), `RequestFlag` (`ReturnOutput`, `ReturnError`), `ExecEnv` for executor environment/sandbox/device setup, `ExecFlag` for collection behavior (`CollectSignal`, `CollectCover`, `DedupCover`, `CollectComps`, `Threaded`), and `CallFlag` for per-call execution status, fault injection, and coverage overflow. `ExecOptsRaw` is a manually aligned 24-byte struct containing env flags, exec flags, and sandbox argument. `ComparisonRaw` is a 32-byte struct with comparison PC, operands, and constness.

Key table object APIs include `ConnectHelloRawT`, `ConnectRequestRawT`, `ConnectReplyRawT`, `InfoRequestRawT`, `InfoReplyRawT`, `FileInfoRawT`, `GlobInfoRawT`, `FeatureInfoRawT`, `ExecRequestRawT`, `ExecutingMessageRawT`, `CallInfoRawT`, `ProgInfoRawT`, `ExecResultRawT`, `StateResultRawT`, `SnapshotHeaderT`, `SnapshotHandshakeT`, and `SnapshotRequestT`. For each table the generated code provides table accessors, `Verify`, object API `UnPack`/`UnPackTo`, `Pack`, a builder, `Create*Raw`, and often `Create*RawDirect`.

## Control Flow
There is no business logic control flow beyond generated serialization helpers. Builders add fields to a `flatbuffers::FlatBufferBuilder`, finish tables, and direct builders allocate strings/vectors. `Verify*` methods walk table fields and vectors to validate serialized buffers. Union verification first checks matching value/type vectors and then dispatches by enum to the table verifier for the concrete message. Union pack/unpack dispatches by the stored enum and reinterpret-casts the stored object to the expected native/table type.

## State And Persistence Behavior
The persistent state is the wire format itself: field numbers, enum numeric values, struct layout, vector ordering, and table offsets are ABI. `HostMessagesRawUnion` and `ExecutorMessagesRawUnion` own heap-allocated native table objects and delete them in `Reset`/destructors. Snapshot coordination fields are explicitly modeled through `SnapshotHeader` state, output offset, and output size; companion Go helpers perform atomic state updates for the Go object API.

## Dependencies And Integration Points
The header depends on FlatBuffers and is consumed by executor C++ code and Go bindings generated from the same schema. It integrates with `pkg/flatrpc/helpers.go`, which aliases generated Go names and adds cloning/sandbox/snapshot helpers, and with `pkg/fuzzer/queue` and `pkg/fuzzer`, which populate `ExecOpts`, `ExecRequest`, and consume `ProgInfo`, `CallInfo`, and result flags.

## Risks
Because this is generated protocol code, manual edits can desynchronize C++ and Go bindings. Enum numeric values and table field positions are wire-compatible contracts. The generated union code relies on enum/type correctness and raw pointer reinterpret casts; stale enum values or mismatched value/type vectors can produce invalid decoding. The FlatBuffers version assertion prevents a known class of compatibility drift, but schema changes still require regenerating all language bindings and checking executor/manager compatibility.

## Test Signals
This header has no direct tests in this item. It is indirectly exercised by fuzzer tests that create `flatrpc.ExecOpts`, `ProgInfo`, `CallInfo`, and queue requests, by executor integration in `TestFuzz`, and by helper tests in adjacent packages. Queue request validation also checks protocol constraints such as mutually exclusive comparison collection and signal/coverage collection.
