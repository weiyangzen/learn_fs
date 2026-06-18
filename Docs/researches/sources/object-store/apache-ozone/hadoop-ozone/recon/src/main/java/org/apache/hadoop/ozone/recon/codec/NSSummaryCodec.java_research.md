## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/NSSummaryCodec.java

Purpose: RocksDB `Codec<NSSummary>` for serializing and deserializing Recon namespace summary records.

Important APIs/types/functions: singleton `get()`; `toPersistedFormatImpl`; `fromPersistedFormatImpl`; `copyObject`; `readParentIdAndReplicatedSize`. It uses primitive codecs for int, short, long, and string fields.

Control flow: serialization writes file counts, size, fixed file-size-bucket length and contents, child directory IDs, directory-name bytes, parent ID, and replicated size. Deserialization reads in that order, then tolerates older persisted records by checking remaining bytes for parent ID and replicated size.

State and persistence: durable binary format for `NSSummary`; schema evolution is handled by optional trailing longs. Dependencies include `ReconConstants.NUM_OF_FILE_SIZE_BINS` and `NSSummary`.

Risks: uses Java `assert` for bucket-length and string-length checks, so production may not enforce corruption checks. `copyObject` reuses arrays/sets rather than deep-copying mutable collections. Tests should verify round-trip, backward compatibility with missing trailing fields, empty directory name, bucket count mismatches, and copy isolation expectations.
