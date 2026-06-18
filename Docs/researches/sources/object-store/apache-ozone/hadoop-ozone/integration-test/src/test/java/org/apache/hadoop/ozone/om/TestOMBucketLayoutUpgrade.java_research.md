# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBucketLayoutUpgrade.java

## Purpose
`TestOMBucketLayoutUpgrade` validates bucket-layout feature gating across OM upgrade finalization. Before finalization, only legacy buckets are allowed; after finalization, all `BucketLayout` values may be created.

## Important APIs, Types, and Functions
- `setup()` starts a three-OM HA cluster initialized at `INITIAL_VERSION`, creates a client and OM protocol proxy, and creates a sample volume.
- Ordered tests are grouped by constants `PRE_UPGRADE`, `DURING_UPGRADE`, and `POST_UPGRADE`.
- `omLayoutBeforeUpgrade()` checks metadata layout version and absence of the persisted layout-version meta-table key.
- `blocksNewLayoutBeforeUpgrade(...)` expects `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION` for non-legacy layouts.
- `allowsLegacyBucketBeforeUpgrade()` and `allowsBucketCreationWithAnyLayoutAfterUpgrade(...)` assert bucket creation and stored layout.
- `finalizeUpgrade()` calls `finalizeUpgrade`, waits for finalization, and waits for `LAYOUT_VERSION_KEY` to equal `maxLayoutVersion()`.

## Control Flow
All test methods share one cluster, so method order matters. The pre-upgrade phase validates initial layout state and allowed/disallowed bucket creation. The during-upgrade phase finalizes the cluster. The post-upgrade phase iterates all enum layouts and verifies creation succeeds and `getBucketInfo` returns the requested layout.

## State and Persistence Behavior
The cluster starts with a testing initial layout version and later persists the finalized layout version in OM metadata. Bucket rows created before and after finalization preserve their requested layouts. The shared cluster means upgrade state intentionally carries across test methods.

## Dependencies and Integration Points
Dependencies include `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, OM layout-version manager, `OMUpgradeTestUtils.waitForFinalization`, Ozone upgrade finalization protocol, `OmBucketInfo`, `OmVolumeArgs`, and JUnit method ordering.

## Risks and Test Signals
Risks include order dependence, shared cluster state, and future enum additions changing pre-upgrade expectations. Signals are exact layout-version metadata checks, `OMException` result code before finalization, finalization reaching done, meta-table layout key matching max layout version, and bucket-info layout equality after creation.
