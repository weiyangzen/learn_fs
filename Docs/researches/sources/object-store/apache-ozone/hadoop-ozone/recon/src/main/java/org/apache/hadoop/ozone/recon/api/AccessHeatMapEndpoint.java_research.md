# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AccessHeatMapEndpoint.java

## Purpose
`AccessHeatMapEndpoint` exposes Recon heatmap APIs for read-access metadata and provider health checks.

## Important APIs, Types, And Functions
The resource is `@Path("/heatmap")`, JSON-producing, `@AdminOnly`, and `@InternalOnly`. It injects `HeatMapServiceImpl`. `getReadAccessMetaData(path, entityType, startDate)` handles `/readaccess`; the overloaded no-arg `getReadAccessMetaData()` handles `/healthCheck`.

## Control Flow
The read-access method checks whether the heatmap feature is disabled through `FeatureProvider.getAllDisabledFeatures()`, then delegates to `heatMapService.retrieveData`. Failures become `WebApplicationException` with HTTP 500. The health-check endpoint directly returns `heatMapService.doHeatMapHealthCheck()`.

## State And Persistence
The endpoint holds only the injected service. Persistence is owned by the heatmap provider/service behind `HeatMapServiceImpl`.

## Dependencies And Integration Points
It integrates REST query constants, `FeatureProvider`, admin filtering via `AdminOnly`, internal feature gating, and heatmap service implementation.

## Risks
The feature-name comparison uses `"HeatMap"` while the annotation uses `"Heatmap"`, so naming consistency matters. Disabled feature returns 404, not a structured feature-disabled body. All service exceptions are collapsed to 500.

## Test Signals
Tests should verify query defaults, disabled-feature 404, successful tree response, service exception mapping, admin filter discovery, and health-check delegation.
