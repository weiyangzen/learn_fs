# sources/object-store/minio/cmd/tier-last-day-stats_gen.go

Purpose: generated msgp serialization implementation for `DailyAllTierStats` and `lastDayTierStats`. It lets rolling tier stats be encoded/decoded efficiently for persistence or inter-node exchange.

Important APIs and functions: for both types, the file implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. `DailyAllTierStats` serializes as a map of tier name to a two-field stat struct. `lastDayTierStats` serializes fields `Bins` and `UpdatedAt`.

Control flow: decoders read map headers, clear or allocate destination maps, dispatch by field name, skip unknown fields, and wrap errors with field paths. `Bins` must decode as an array of exactly 24 elements; mismatches return `msgp.ArrayError`. Encoders write map/array headers and delegate each `tierStats` bin to its generated msgp methods.

State and persistence: no independent state; this code defines the wire/storage representation of daily tier stats. It preserves forward compatibility by skipping unknown fields but is strict on the fixed bin array length.

Dependencies and integration points: depends on `github.com/tinylib/msgp/msgp` and generated msgp support for `tierStats`. It is generated from `tier-last-day-stats.go` via the `msgp` directive and must stay in sync with struct fields.

Risks: manual edits will be overwritten. Changing the number of bins or field names requires regeneration and compatibility review. Map iteration order is intentionally nondeterministic for maps, so tests should not depend on byte-for-byte order for multi-entry maps unless sorted elsewhere.

Test signals: `tier-last-day-stats_gen_test.go` checks marshal/unmarshal, encode/decode, skip behavior, msg size bounds, and benchmarks generated paths.
