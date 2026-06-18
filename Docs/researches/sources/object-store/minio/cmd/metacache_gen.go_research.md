# sources/object-store/minio/cmd/metacache_gen.go

Purpose: This generated file implements msgp serialization for `metacache` and `scanStatus`, defining the compact persisted/transport representation of listing cache state.

Important APIs and types: It provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*metacache`, plus the same methods for `scanStatus`. Encoded metacache keys use short msg tags: `end`, `st`, `lh`, `u`, `b`, `flt`, `id`, `err`, `root`, `fnf`, `stat`, `rec`, and `v`.

Control flow: Decode/Unmarshal read msgpack maps and assign timestamp, string, bool, uint8, and status fields while skipping unknown keys. Encode/Marshal write a fixed 13-field map. `scanStatus` is encoded as a uint8.

State and persistence behavior: This file does not make state transitions itself, but it controls durable metacache field compatibility. It preserves timestamps, status, error, bucket/id/root/filter, recursive mode, file-not-found state, and stream version. Any field not represented here will not survive manager persistence or peer transport.

Dependencies and integration points: It depends on `tinylib/msgp/msgp` and the production `metacache` definitions. Cache managers, peer update calls, and tests rely on this binary contract.

Risks: Manual edits are unsafe because regeneration will overwrite them. Reordering or retagging fields can break mixed-version compatibility. `scanStatus` has no validation in generated decode, so unknown numeric states can enter memory if read from corrupt or future payloads.

Test signals: `metacache_gen_test.go` validates zero-value marshal/unmarshal, skip, stream encode/decode, `Msgsize` sanity, and benchmarks. Behavioral status transitions are tested in `metacache_test.go`, not here.
