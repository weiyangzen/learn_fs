# sources/object-store/minio/cmd/bootstrap-peer-server_gen.go

This generated msgp file serializes `ServerSystemConfig`, the bootstrap peer verification payload. It implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

The encoded schema is a four-field map: `NEndpoints` as int, `CmdLines` as an array of strings, `MinioEnv` as a string-to-string map, and `Checksum` as string. Decoders read map keys and skip unknown fields, which allows extra future fields to be ignored by older readers. Slice and map decoders reuse existing allocations where possible and explicitly nil out fields when encoded lengths are zero.

This serialization is part of startup configuration verification over MinIO's grid transport. It does not persist durable state, but incorrect serialization can cause peers to reject each other or miss real mismatches. The payload intentionally contains hashed environment values rather than raw secrets, but command lines and env key names may still be operationally sensitive.

Dependencies are `github.com/tinylib/msgp/msgp` and the `ServerSystemConfig` type in `bootstrap-peer-server.go`. Test coverage in `bootstrap-peer-server_gen_test.go` verifies zero-value marshal/unmarshal, stream encode/decode, skip behavior, and benchmark allocation profiles. Missing coverage includes non-empty command-line arrays, non-empty environment maps, unknown fields, and mismatched schema compatibility.
