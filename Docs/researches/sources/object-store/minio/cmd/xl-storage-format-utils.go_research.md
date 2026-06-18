# sources/object-store/minio/cmd/xl-storage-format-utils.go

Converts raw xl.meta buffers into `FileInfo` and `FileInfoVersions` and provides deterministic weak metadata hashing. It supports indexed meta v2 fast paths and non-indexed `xlMetaV2.LoadOrConvert` fallback.

`getFileInfoVersions` partitions tier free versions unless inclusion is requested and updates `NumVersions`. `getAllFileInfoVersions` synthesizes a latest delete marker with `timeSentinel1970` when metadata has no versions. `getFileInfo` handles optional inline data extraction, null version IDs, and legacy `DataDir` fallback. Hash helpers use salted xxh3 values in an order-independent xor scheme.

Risks include free-version partition mistakes, synthetic delete marker semantics, inline data lookup drift, and weak hash collisions. Tests cover deterministic string hashing and free-version filtering/order, but not indexed meta, inline data, or byte-map hashing.
