<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java

## Purpose

`FeaturesEndpoint` exposes Recon feature-gating metadata under `/features`, currently the admin-only `/disabledFeatures` API.

## Important APIs and Types

The endpoint is a JAX-RS resource annotated with `@Path("/features")`, `@Produces(APPLICATION_JSON)`, and `@AdminOnly`. Its only operation, `getDisabledFeatures`, returns `FeatureProvider.getAllDisabledFeatures()` as the response entity.

## Control Flow

Requests enter `getDisabledFeatures`, which asks `FeatureProvider` for all disabled features, logs them, and returns HTTP 200. Any exception is wrapped as a `WebApplicationException` with HTTP 500.

## State and Persistence

The class stores injected `OzoneConfiguration`, but the current method does not read it. It has no persistence and no mutable endpoint state.

## Dependencies and Integration Points

It integrates with Recon's admin authorization filter via `@AdminOnly`, with `FeatureProvider.Feature` DTOs for UI/API clients, and with JAX-RS exception handling.

## Risks and Edge Cases

The logger is initialized with `HeatMapServiceImpl.class`, so log category ownership is misleading. Because `ozoneConfiguration` is unused, future feature gating may need cleanup or tests to detect stale injection. The endpoint trusts `FeatureProvider` to return serializable feature data.

## Test Signals

Tests should assert admin-only binding, JSON shape for enabled/disabled feature lists, and HTTP 500 behavior when `FeatureProvider` fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/FeaturesEndpoint.java -->
