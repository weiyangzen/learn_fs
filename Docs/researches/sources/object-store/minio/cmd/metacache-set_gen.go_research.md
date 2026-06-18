# sources/object-store/minio/cmd/metacache-set_gen.go

Purpose: This generated file implements the `tinylib/msgp` serialization contract for `listPathOptions`, the transport/persistence shape used when listing options are sent across storage RPCs or encoded for metacache coordination.

Important APIs and types: It provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*listPathOptions`. Encoded fields are `ID`, `Bucket`, `BaseDir`, `Prefix`, `FilterPrefix`, `Marker`, `Limit`, `AskDisks`, `InclDeleted`, `Recursive`, `Separator`, `Create`, `IncludeDirectories`, `Transient`, `Versioned`, `V1`, `StopDiskAtLimit`, and the unexported `pool` and `set` integers.

Control flow: Decode reads a msgpack map header, switches on string keys, assigns known fields, and skips unknown keys for forward compatibility. Encode writes a fixed map of 19 fields. Marshal appends the same map into a caller-provided byte slice using `msgp.Require`; Unmarshal reads from a byte slice and returns the unconsumed tail. `Msgsize` computes an upper-bound allocation estimate.

State and persistence behavior: This file does not own storage state, but it defines which `listPathOptions` fields survive serialization. Runtime-only fields marked `msg:"-"` in the source type, such as lifecycle, versioning, retention, and replication config pointers, are intentionally absent and must be rehydrated on the receiving side if needed.

Dependencies and integration points: The generated code depends only on `github.com/tinylib/msgp/msgp` and the source `listPathOptions` type. It is used by grid/peer/listing code paths that need compact binary option transport and by generated tests that guard marshal/unmarshal behavior.

Risks: Manual edits would be overwritten by `go generate`. Adding a field to `listPathOptions` requires regenerating this file and considering whether that field should be serialized. Including unexported `pool` and `set` is intentional for local routing but creates a compatibility surface across mixed-version nodes.

Test signals: `metacache-set_gen_test.go` checks zero-value marshal/unmarshal, `msgp.Skip`, encode/decode, `Msgsize` sanity, and benchmark paths. Those tests do not populate all fields, so non-zero field round-trip coverage depends on broader integration tests or msgp generator correctness.
