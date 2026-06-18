# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotWithoutBucketLinkingLegacy.java

Purpose: This concrete subclass runs the shared snapshot suite for legacy bucket layout without linked buckets. It preserves regression coverage for pre-FSO bucket semantics.

Important APIs/types/functions: The class extends `TestOmSnapshot`, imports `BucketLayout.LEGACY`, and calls `super(LEGACY, false, false, false, false)`.

Control flow: The inherited suite runs with legacy layout, filesystem paths disabled, full diff disabled, native diff enabled if available, and linked buckets disabled. Legacy-specific behavior is handled by `bucketLayout` branches in the base test.

State and persistence behavior: Snapshot state is represented through the legacy/key-table model rather than FSO file and directory tables. Tests cover point-in-time reads, diff operations, deletion protection, quota neutrality, tag/metadata modifications, stream key behavior, and MPU behavior under that layout.

Dependencies and integration points: This subclass connects the base snapshot suite with legacy bucket metadata, OM key table diffing, object-store-style listing, and MiniOzone cluster setup.

Risks and edge cases: Legacy layout may differ from FSO in directory materialization and diff ordering. The subclass name emphasizes no bucket linking; linked-bucket edge cases are covered elsewhere.

Test signals: Passing inherited tests confirm legacy snapshot behavior remains compatible with create/list/read/delete/diff, restart, and mutation scenarios.
