# sources/object-store/minio/cmd/tier_gen.go

Purpose: generated msgp serializer for `TierConfigMgr`. It serializes only the persistent `Tiers` map and deliberately omits mutexes, driver cache, and refresh timestamp according to struct tags.

Important APIs and functions: implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*TierConfigMgr`. The encoded object is a one-field map containing `"Tiers"`, with string keys and `madmin.TierConfig` values.

Control flow: decoders allocate or clear `z.Tiers`, read each tier name and delegate value decoding to `madmin.TierConfig.DecodeMsg`/`UnmarshalMsg`, skip unknown fields, and wrap errors with field/key context. Encoders write the one-field map and iterate over `z.Tiers`.

State and persistence: this code defines the serialized body used by `TierConfigMgr.Bytes` after the four-byte format/version header. It does not serialize `drivercache` or `lastRefreshedAt`, so those are reconstructed after load.

Dependencies and integration points: depends on `madmin-go/v3` generated msgp support and `tinylib/msgp`. It is generated from `tier.go` and consumed by tier config save/load paths.

Risks: map iteration order is nondeterministic, so serialized byte order can vary for multiple tiers. Field-name changes or moving persistence-relevant fields without regenerating can break config compatibility. Because driver cache is omitted, load paths must always initialize or rebuild `drivercache`.

Test signals: `tier_gen_test.go` validates empty-value marshal/unmarshal and encode/decode paths. Production load/save paths add coverage for real tier configs when admin tier tests exist.
