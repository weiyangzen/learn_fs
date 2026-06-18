# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/OldSnapshotDiffJobCodecForTesting.java

Purpose: provides a test-only implementation of the old JSON `Codec<SnapshotDiffJob>` for compatibility testing.

Important APIs/types/functions: implements `getTypeClass`, `toPersistedFormatImpl`, `fromPersistedFormatImpl`, and `copyObject`. Serialization uses Jackson `ObjectMapper` configured to omit nulls and ignore unknown properties.

Control flow and state: stateless aside from a static mapper. Encoding writes `SnapshotDiffJob` as JSON bytes; decoding reads JSON bytes back. `copyObject` returns the same object and explicitly is not a deep copy.

Dependencies and integration points: used by `TestOmSnapshotDiffJobCodec` to generate legacy persisted data so the current `SnapshotDiffJob.codec()` can prove backward compatibility.

Risks and test signals: the main risk is divergence from the historical codec shape. Since this is a compatibility fixture, changes should be avoided unless the legacy format definition itself was wrong.
