# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestFeaturesEndPoint.java

## Purpose
Focused unit/integration test for `FeaturesEndpoint.getDisabledFeatures`, currently centered on whether the Recon heatmap feature appears in the disabled-feature list based on provider class configuration and the heatmap enable flag.

## Important APIs, types, and functions
- Endpoint under test is `FeaturesEndpoint.getDisabledFeatures`.
- Uses `FeatureProvider.initFeatureSupport(OzoneConfiguration)` to refresh static feature availability before each assertion.
- Reads configuration keys `OZONE_RECON_HEATMAP_PROVIDER_KEY` and `OZONE_RECON_HEATMAP_ENABLE_KEY`.
- Builds a minimal `ReconTestInjector` with temporary Recon OM metadata, SQL DB, container DB, SCM facade binding, and storage/OM service provider mocks.

## Control flow
`initializeInjector` creates an `OzoneConfiguration`, temporary OM metadata manager, Recon test injector, and endpoint instance. Tests mutate the same configuration, call `FeatureProvider.initFeatureSupport`, fetch disabled features, cast the response entity to a list of `FeatureProvider.Feature`, and assert whether `FeatureProvider.Feature.HEATMAP` is present or the list is empty.

## State and persistence behavior
The only meaningful state is static feature-support state inside `FeatureProvider`, refreshed from the mutable `OzoneConfiguration`. Temporary OM, SQL, and container DB state exists only to satisfy endpoint injection and is not inspected. Because setup is guarded by `isSetupDone`, the endpoint and configuration are reused within the test instance while each test explicitly reinitializes feature support.

## Dependencies and integration points
The file touches Recon dependency injection, OM metadata test utilities, SCM facade binding, `FeatureProvider` feature detection, and JAX-RS `Response` entities. It verifies the API-level representation of feature gating rather than heatmap provider behavior itself.

## Risks and edge cases
The test depends on static mutable feature state, so missing `initFeatureSupport` calls or parallel test execution could affect isolation. It asserts the first disabled feature is heatmap when disabled; adding other disabled features with earlier ordering may require a less order-sensitive assertion. The valid provider class name is hard-coded to the test heatmap provider implementation.

## Test signals
Signals are simple: empty provider string disables heatmap, valid provider plus enabled flag returns no disabled features, valid provider plus disabled flag includes heatmap, and valid provider plus true flag excludes heatmap.
