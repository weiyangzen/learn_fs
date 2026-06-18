# sources/object-store/minio/cmd/background-newdisks-heal-ops_gen.go

Purpose: Generated `tinylib/msgp` serialization for `healingTracker`, used by `background-newdisks-heal-ops.go` to persist disk-healing progress in `.healing.bin`.

Important APIs/types/functions: Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*healingTracker`. The serialized map has 29 fields: ID, pool/set/disk indexes, path, endpoint, started/last update times, object totals, healed/failed/skipped item and byte counters, bucket/object cursor, resume counters, queued/healed buckets, heal ID, retry attempts, and finished flag.

Control flow: Decode/unmarshal reads a msgpack map, switches on string field names, populates primitive fields, resizes bucket slices, and skips unknown fields for forward compatibility. Encode/marshal writes the same fixed field set in generated order. `Msgsize` computes an upper-bound allocation estimate used by `MarshalMsg`.

State/persistence behavior: The file defines the binary compatibility boundary for on-disk healing trackers. Fields with `msg:"-"` in the source type, such as `disk` and mutex, are intentionally omitted and must be reattached after load. Because unknown fields are skipped, older binaries can ignore newer fields, but missing fields fall back to Go zero values.

Dependencies/integration: Depends only on `github.com/tinylib/msgp/msgp` and the source `healingTracker` type. It is called by `loadHealingTracker`, `save`, and any code that writes or reads `.healing.bin`.

Risks/test signals: Manual edits would be overwritten by `go generate`. Schema changes in `healingTracker` must regenerate this file or persisted state will diverge. Generated tests verify marshal/unmarshal, streaming encode/decode, skip behavior, and benchmark allocation/performance, but they only use zero-value data and do not test compatibility with real tracker payloads.
