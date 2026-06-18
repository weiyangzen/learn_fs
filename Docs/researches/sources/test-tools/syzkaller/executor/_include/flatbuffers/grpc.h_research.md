# sources/test-tools/syzkaller/executor/_include/flatbuffers/grpc.h

## Purpose

`grpc.h` glues FlatBuffers buffers to C++ gRPC transport primitives. It wraps `grpc::Slice` in a typed FlatBuffers message, provides a `FlatBufferBuilder` variant backed by gRPC slice allocation, and specializes gRPC `SerializationTraits`.

## Important APIs, Types, and Functions

`flatbuffers::grpc::Message<T>` is a move-only typed wrapper with `data`, `mutable_data`, `size`, `Verify`, `GetRoot`, `GetMutableRoot`, and `BorrowSlice`. `SliceAllocator` implements `Allocator` with one refcounted `grpc::Slice`. `MessageBuilder` derives from `FlatBufferBuilder`, owns a `SliceAllocator`, supports moves and conversion from a default-allocator `FlatBufferBuilder`, and exposes `Swap`, `ReleaseRaw`, `GetMessage<T>`, and `ReleaseMessage<T>`. `grpc::SerializationTraits<flatbuffers::grpc::Message<T>>` serializes/deserializes messages to/from `ByteBuffer`.

## Control Flow

Outgoing messages are built in `MessageBuilder`; allocation and growth operate on `grpc::Slice` memory. `GetMessage<T>` calculates the FlatBuffers payload subrange, creates a subslice, and wraps it as `Message<T>`. gRPC serialization borrows the slice into a one-slice `ByteBuffer`. Incoming deserialization obtains a single slice via `TrySingleSlice` or `DumpToSingleSlice`, clears the source buffer, assigns the message, and verifies it unless `FLATBUFFERS_GRPC_DISABLE_AUTO_VERIFICATION` is defined.

## State and Persistence Behavior

State is refcounted slice ownership. `Message<T>` is move-only to avoid ambiguous ownership. `SliceAllocator` assumes one active allocation and asserts pointer/size matches. `MessageBuilder::Swap` restores embedded allocator identity after swapping builder state.

## Dependencies and Integration Points

It depends on `flatbuffers/flatbuffers.h`, `grpcpp/support/byte_buffer.h`, and `grpcpp/support/slice.h`. It integrates generated roots through `Verifier::VerifyBuffer<T>`, `GetRoot<T>`, and `GetMutableRoot<T>`, and with gRPC through `SerializationTraits`.

## Risks and Edge Cases

The allocator is specialized for one buffer at a time. Conversion from a normal `FlatBufferBuilder` supports the default allocator path. `mutable_data` allows mutation of slice-backed memory, which should be controlled once shared. Disabling auto-verification allows invalid RPC payloads through.

## Test Signals

Tests should build a generated FlatBuffer with `MessageBuilder`, serialize/deserialize through `ByteBuffer`, verify the root, cover multi-slice input fallback, invalid payload verification, moves, `ReleaseRaw`, and conversion from `FlatBufferBuilder`.
