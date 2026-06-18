# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/FileSizeCountKey.java

Purpose: Composite RocksDB key for file-size count rows, grouping by volume, bucket, and file-size upper bound.

Important APIs/types: immutable fields `volume`, `bucket`, `fileSizeUpperBound`; `getCodec`; protobuf conversion methods `toProto` and `fromProto`; value getters; `equals`, `hashCode`, and `toString`.

State and persistence: persisted with a `DelegatedCodec` over `FileSizeCountKeyProto`. The key is used in `ReconDBDefinition.FILE_COUNT_BY_SIZE` and therefore its serialized field order and presence semantics are storage compatibility concerns.

Dependencies and integration: created by `FileSizeCountTaskHelper.getFileSizeCountKey` using OM key volume/bucket and `ReconUtils.getFileSizeUpperBound`. Consumed by `ReconFileMetadataManagerImpl` for RocksDB operations.

Risks: constructor accepts null values but equality/hash/protobuf setters do not tolerate null volume/bucket/upper bound. Changing proto fields or binning semantics breaks existing RocksDB rows. The key does not include bucket layout, relying on volume/bucket identity to distinguish logical buckets.

Test signals: codec round-trip, equality/hash map behavior, and all expected file-size upper-bound bins should be covered. Tests should reject or document null handling.
