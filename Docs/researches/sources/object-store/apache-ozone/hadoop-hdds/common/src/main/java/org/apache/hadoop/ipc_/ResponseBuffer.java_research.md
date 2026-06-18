
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ResponseBuffer.java

## Purpose

`ResponseBuffer` is a reusable byte buffer for length-framed RPC responses. It reserves four leading bytes for payload length and writes response data after that frame header.

## Important APIs, types, and functions

Constructors create a `FramedBuffer` with default or explicit capacity. `writeTo(OutputStream)` updates the frame length and writes the whole framed buffer. Package-visible helpers include `toByteArray()`, `capacity()`, `setCapacity()`, `ensureCapacity()`, and `reset()`. `FramedBuffer` overrides `size()` and `reset()` and writes the big-endian frame length in `setSize()`.

## Control flow

RPC writable wrappers write payload bytes to the `DataOutputStream`. Before output, `getFramedBuffer()` sets the first four bytes to `written`, then the buffer is emitted. `reset()` clears the logical payload and returns the write pointer to just after the framing bytes.

## State and persistence behavior

State is in-memory byte array capacity, byte count, and `DataOutputStream.written`. No data is persisted.

## Dependencies and integration points

It is used by `RpcWritable` and server response encoding paths to avoid extra intermediate arrays and to preserve Hadoop RPC length framing.

## Risks and test signals

Capacity changes must preserve the four framing bytes and existing payload when appropriate. Tests should cover empty response framing, big-endian length bytes, `ensureCapacity()` growth, `reset()` reuse, `writeTo()` length correctness, and large protobuf/writable payloads.
