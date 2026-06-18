# sources/object-store/minio/cmd/xl-storage-format-v1_gen_test.go

Generated msgp tests and benchmarks for legacy XL metadata v1 serialization. For each generated type, tests marshal/unmarshal, ensure no leftover bytes, ensure `msgp.Skip` consumes the object, encode/decode through streaming APIs, and warn if `Msgsize` underestimates output length. Benchmarks cover marshal, append marshal, unmarshal, encode, and decode.

All fixtures are zero-value in-memory instances. The tests catch generated-code breakage but do not cover non-zero compatibility fixtures, malformed data, or semantic metadata validity.
