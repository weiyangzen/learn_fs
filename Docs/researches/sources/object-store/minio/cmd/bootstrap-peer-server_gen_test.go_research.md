# sources/object-store/minio/cmd/bootstrap-peer-server_gen_test.go

This generated test file validates msgp serialization for `ServerSystemConfig`. It follows the standard generated pattern used elsewhere in this subset.

`TestMarshalUnmarshalServerSystemConfig` marshals a zero-value config, unmarshals it, checks for no leftover bytes, and verifies `msgp.Skip` consumes the whole payload. `TestEncodeDecodeServerSystemConfig` encodes through the streaming API, logs if `Msgsize` underestimates the encoded length, decodes into a new config, then tests reader-level skip. Benchmarks cover marshal, append marshal, unmarshal, stream encode, and stream decode with allocation reporting.

The tests create no durable state and depend only on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. Their integration value is protecting the generated codec used by bootstrap grid verification.

Risk coverage is limited because the fixture is zero-value. It does not validate non-empty `CmdLines`, non-empty `MinioEnv`, checksum strings, map ordering effects, unknown fields, or compatibility with older serialized configs. Operational bootstrap correctness is tested elsewhere, if at all; this file only proves the generated methods are structurally usable.
