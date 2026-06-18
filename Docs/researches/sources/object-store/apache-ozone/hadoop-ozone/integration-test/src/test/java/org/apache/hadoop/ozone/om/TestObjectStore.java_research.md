# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStore.java

Purpose: This abstract non-HA integration test verifies object-store bucket layout behavior when filesystem path handling is not the focus. It checks explicit bucket layouts, default layout selection, link bucket layout resolution, dangling link behavior, and loop detection for linked buckets.

Important APIs and types: The test uses the `NonHATests.TestCase` cluster contract, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `BucketArgs`, `BucketLayout`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, and `OMException` result code `DETECTED_LOOP_IN_BUCKET_LINKS`.

Control flow: `init` takes the shared non-HA cluster config and client. `testCreateBucketWithBucketLayout` creates a volume and then buckets with no layout, `OBJECT_STORE`, `LEGACY`, and `FILE_SYSTEM_OPTIMIZED`, verifying each returned bucket layout. Link tests create source buckets of different layouts, create link buckets by setting source volume/bucket with `BucketLayout.DEFAULT`, and inspect resolved layout through `getBucket`. The dangling link test points at a missing source and expects the default layout. The loop test creates three link buckets that reference one another and expects lookup to fail.

State and persistence behavior: Persistent state is volume/bucket metadata, including bucket layout, link source volume/bucket fields, and link-chain relationships. The test observes that link buckets inherit the resolved source layout when possible, while dangling links fall back to the current configured default.

Dependencies and integration points: It covers client object-store APIs, OM bucket creation and lookup, bucket layout defaults, link bucket resolution, and loop detection in link traversal. It is intended to run under the non-HA test harness configuration.

Risks: Default-layout expectations depend on the surrounding non-HA cluster configuration. Link-chain checks validate client-visible metadata rather than raw DB records. The loop test intentionally constructs invalid metadata through normal API calls, so future stricter creation-time validation could shift the failure point.

Test signals: Signals are exact layout equality for each bucket creation mode, link bucket layouts matching source bucket layouts including chained links, dangling source name preservation with default layout fallback, and `DETECTED_LOOP_IN_BUCKET_LINKS` when resolving a cyclic link chain.
