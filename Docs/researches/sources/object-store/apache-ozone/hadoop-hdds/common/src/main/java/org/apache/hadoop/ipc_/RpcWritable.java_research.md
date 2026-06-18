
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcWritable.java

## Purpose

`RpcWritable` is the optimized serialization adapter used by Hadoop IPC for `Writable`, protobuf `Message`, and raw byte-buffer RPC payloads.

## Important APIs, types, and functions

`wrap(Object)` returns an existing `RpcWritable`, a `ProtobufWrapper`, or a `WritableWrapper`. Standard `Writable.readFields()` and `write()` are final and unsupported to force optimized paths. `writeTo(ResponseBuffer)` and `readFrom(ByteBuffer)` are the core internal methods.

`WritableWrapper` delegates serialization to a `Writable` and reads through a `DataInputStream` over a byte-array-backed buffer. `ProtobufWrapper` writes/reads delimited protobuf messages using `CodedOutputStream`/`CodedInputStream`. `Buffer` wraps raw bytes, can instantiate configured value classes, decodes values with `getValue()`, and exposes remaining bytes.

## Control flow

Client and server code wrap response/request objects, write them to `ResponseBuffer`, or receive a `Buffer` and lazily decode it into the expected type. Protobuf decoding consumes only the delimited message and advances the `ByteBuffer` by bytes read. Writable decoding advances the buffer based on consumed bytes.

## State and persistence behavior

Wrappers hold either a mutable protobuf message reference, a writable instance, or a `ByteBuffer` slice. State is per-call and in-memory.

## Dependencies and integration points

It integrates `ResponseBuffer`, Hadoop `Writable`, `Configurable`, `Configuration`, protobuf `Message`, and IPC client/server request decoding. `ProtobufRpcEngine.RpcProtobufRequest` extends `RpcWritable.Buffer`.

## Risks and test signals

The implementation assumes byte-array-backed `ByteBuffer`s. Position/limit advancement is subtle and affects multi-message protobuf request decoding. `valueClass.newInstance()` requires a no-arg constructor. Tests should cover writable round trips, protobuf delimited round trips, buffer slicing, multiple values in one buffer, configurable instantiation, unsupported legacy methods, and direct-buffer rejection or avoidance.
