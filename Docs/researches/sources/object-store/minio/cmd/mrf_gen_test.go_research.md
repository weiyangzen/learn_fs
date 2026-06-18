# sources/object-store/minio/cmd/mrf_gen_test.go

This file tests and benchmarks msgp serialization generated for `PartialOperation`. It does not test MRF queue behavior, healing, or shutdown persistence, but it verifies that the generated codecs can round-trip an empty `PartialOperation` and that msgp skip handling consumes the encoded payload fully.

The main tests are `TestMarshalUnmarshalPartialOperation` and `TestEncodeDecodePartialOperation`. The first marshals a zero-value operation to bytes, unmarshals it, asserts no trailing bytes remain, then verifies `msgp.Skip` also consumes the full buffer. The second encodes through the streaming `msgp.Encode` path, checks whether `Msgsize` underestimates, decodes into a new value, and checks that a reader can skip the encoded message.

Benchmarks cover allocation and throughput for `MarshalMsg`, append-style marshal reuse, `UnmarshalMsg`, streaming `EncodeMsg`, and streaming `DecodeMsg`. They use zero-value data, so they primarily measure framework overhead and fixed field encoding rather than large bucket/object names or version byte arrays.

Dependencies are Go `testing`, `bytes`, and `tinylib/msgp`. Integration point is the generated `mrf_gen.go` codec consumed by `mrf.go` persistence. Risks: tests do not cover non-empty fields, malformed headers from the persistence file, forward-compatible unknown fields, or version-byte UUID content. Still, they provide a basic regeneration guard for msgp API correctness.
