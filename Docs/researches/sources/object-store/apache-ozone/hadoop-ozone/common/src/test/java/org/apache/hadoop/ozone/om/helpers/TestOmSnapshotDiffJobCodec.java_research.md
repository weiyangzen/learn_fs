# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotDiffJobCodec.java

Purpose: verifies the current `SnapshotDiffJob` codec can read JSON data persisted by the old Jackson-based codec.

Important APIs/types/functions: uses `OldSnapshotDiffJobCodecForTesting.toPersistedFormatImpl`, `SnapshotDiffJob.codec()`, and `fromPersistedFormatImpl`. It inspects job ID, status, volume, bucket, snapshots, full-diff flags, native-diff flag, sub-status, total entries, largest entry key, and progress percent.

Control flow and state: constructs a `SnapshotDiffJob`, serializes it using the old codec, decodes it with the new codec, and compares critical fields. The test expects `keysProcessedPct` to be `0.0` after fallback decoding.

Dependencies and integration points: integrates with snapshot diff response `JobStatus` and `SubStatus`, HDDS DB codec APIs, and legacy RocksDB persisted JSON format.

Risks and test signals: protects rolling upgrade/backward compatibility for existing snapshot diff jobs. Any change to new codec fallback logic should preserve this test or include migration handling.
