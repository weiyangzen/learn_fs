# sources/object-store/minio/cmd/batch-rotate_gen_test.go

This generated test file verifies the msgp methods for key-rotation job types. It covers `BatchJobKeyRotateEncryption`, `BatchJobKeyRotateFlags`, `BatchJobKeyRotateV1`, `BatchKeyRotateFilter`, and `BatchKeyRotateNotification` with round-trip and benchmark scaffolding.

Each `TestMarshalUnmarshal...` uses a zero-value object, marshals it to bytes, unmarshals it, checks that no bytes are left over, and verifies `msgp.Skip` consumes the payload. Each `TestEncodeDecode...` streams the value through `msgp.Encode`/`msgp.Decode`, logs if `Msgsize` is smaller than the actual buffer, and checks reader `Skip`. Benchmarks measure allocation and throughput for marshal, append marshal, unmarshal, stream encode, and stream decode.

The tests do not create persistent state, but they exercise generated code used for persisted batch key-rotation definitions. Their dependencies are `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`.

The strongest test signal is that generated methods compile and can process the zero-value schema without leftover bytes. Important gaps remain: no non-zero `Type`, `Key`, base64 `Context`, filters, tags, metadata, KMS key IDs, notify endpoint/token, retry values, or full `BatchJobKeyRotateV1` fixtures are asserted. There is also no compatibility fixture for older serialized jobs or unknown-field handling. These tests should be treated as generated-code smoke tests, not validation of batch rotation semantics.
