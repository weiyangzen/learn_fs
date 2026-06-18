# sources/object-store/minio/cmd/metacache-walk_gen.go

Purpose: This generated file implements `tinylib/msgp` serialization for `WalkDirOptions`, the request payload used to invoke disk walking locally and over storage REST/grid streams.

Important APIs and types: It defines `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*WalkDirOptions`. The encoded map contains `Bucket`, `BaseDir`, `Recursive`, `ReportNotFound`, `FilterPrefix`, `ForwardTo`, `Limit`, and `DiskID`.

Control flow: Decode and Unmarshal switch on msgpack map keys, assign known fields, and skip unknown fields. Encode and Marshal write a fixed 8-field map. `Msgsize` estimates the serialized size for preallocation.

State and persistence behavior: No storage is modified. The file defines the binary compatibility boundary for remote disk walks, including the disk identity check value that prevents a client from streaming from the wrong physical disk after replacement.

Dependencies and integration points: It depends on `github.com/tinylib/msgp/msgp` and the `WalkDirOptions` type. `storageRESTClient.WalkDir` calls `MarshalMsg` before opening `grid.HandlerWalkDir`, and `storageRESTServer.WalkDirHandler` calls `UnmarshalMsg` before validating disk ID and invoking `xlStorage.WalkDir`.

Risks: Any field added to `WalkDirOptions` must be regenerated and reviewed for mixed-version behavior. Because remote walks are performance-sensitive, `Msgsize` and allocation behavior matter. Unknown-field skipping helps forward compatibility, but missing fields default to zero values that can change traversal semantics.

Test signals: `metacache-walk_gen_test.go` covers zero-value marshal/unmarshal, skip, encode/decode, `Msgsize` warning, and serialization benchmarks.
