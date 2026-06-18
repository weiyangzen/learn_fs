# sources/object-store/minio/cmd/xl-storage-format-v1.go

Defines legacy XL metadata v1 schema and helpers. `xlMetaV1Object` models persisted metadata, including stat, erasure information, release, user metadata, parts, and dummy version/data-dir fields. Supporting types include `StatInfo`, `ErasureInfo`, `ObjectPartInfo`, `ChecksumInfo`, and `BitrotAlgorithm`.

Validation checks version/format and erasure data/parity blocks. `ErasureInfo.Equal` compares cluster-significant erasure settings. `ChecksumInfo` has custom JSON marshal/unmarshal for `part.N`, algorithm names, and hex hashes. `ToFileInfo` converts valid v1 metadata to `FileInfo` with `XLV1` and one version. `Signature` zeroes disk-local fields, hashes metadata deterministically, msgp-serializes, and folds xxhash into four bytes.

This code is persisted-format compatibility code. Risks include signature instability, legacy decoding drift, checksum parser errors, and weak signature collisions. Generated msgp tests cover serialization basics, not all semantic validation.
