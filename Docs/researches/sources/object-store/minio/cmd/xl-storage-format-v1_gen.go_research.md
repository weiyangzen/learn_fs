# sources/object-store/minio/cmd/xl-storage-format-v1_gen.go

Generated `msgp` serialization for legacy XL metadata v1 types: `BitrotAlgorithm`, `ChecksumInfo`, `ErasureInfo`, `ObjectPartInfo`, `StatInfo`, `checksumInfoJSON`, and `xlMetaV1Object`.

Each type implements decode, encode, marshal, unmarshal, and message-size estimation. The code skips unknown fields, wraps field-path errors, reuses slices/maps, clears maps before refill, and resets omitted optional `ObjectPartInfo` fields when absent.

It is pure serialization but defines persisted compatibility. Do not hand-edit except through generation. Risks include field tag/schema drift and omitted-field clearing regressions. Generated tests provide zero-value round-trip and benchmark coverage.
