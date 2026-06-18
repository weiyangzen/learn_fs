# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/FeatureProvider.java

## Purpose
Static feature metadata provider for Recon feature availability, currently tracking whether HeatMap should be disabled based on configuration.

## Important APIs, Types, And Functions
declares `FeatureProvider`, `Feature`; key fields include `featureDisableMap`, `featureName`; important methods include `getFeatureName`, `of`, `getFeatureDisableMap`, `getAllDisabledFeatures`, `initFeatureSupport`, `resetInitOfFeatureSupport`.

## Control Flow
`initFeatureSupport` resets the disable map then disables HeatMap when the heatmap feature flag is false or no provider class is configured.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Ozone configuration. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are static mutable feature state shared across tests/process lifetime and `Feature.of` throwing `NoSuchElementException` before its explicit invalid-value error path.

## Test Signals
Tests should cover enabled/disabled config combinations and the `Feature.of` invalid-name path, which currently uses `findFirst().get()` before its explicit error branch.
