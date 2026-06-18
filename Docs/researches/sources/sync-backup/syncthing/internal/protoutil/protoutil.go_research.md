# sources/sync-backup/syncthing/internal/protoutil/protoutil.go

Purpose: Small protobuf marshaling helper for writing into caller-provided buffers without unexpected allocation.

Important APIs/types/functions: `MarshalTo(buf []byte, pb proto.Message) (int, error)` checks `proto.Size(pb)` against `len(buf)`, returns `errBufferTooSmall` when insufficient, returns zero for zero-size messages, then uses `proto.MarshalOptions.MarshalAppend(buf[:0], pb)`.

Control flow: After marshaling, it compares the first element address of the original buffer and returned slice. If they differ, it panics because the earlier size check should have prevented reallocation.

State and persistence behavior: Stateless. It serializes protobuf messages into transient buffers, likely on network or storage hot paths.

Dependencies and integration points: Depends on `google.golang.org/protobuf/proto`. Integrates with generated protobuf messages across Syncthing.

Risks: `errBufferTooSmall` is package-private, so callers can only compare by error string unless they are in-package. The address check relies on non-empty buffers and is bypassed for zero-size protobufs. Callers must use the returned byte count rather than assuming the whole buffer was filled.

Test signals: No direct test in this subset. Useful tests would cover too-small buffers, exact-fit buffers, zero-size messages, and marshal errors.
