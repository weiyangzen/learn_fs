<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java

## Purpose

`VolumeEndpoint` exposes paginated Recon OM volume metadata.

## Important APIs and Types

`GET /volumes` accepts `limit` and `prevKey` query parameters using Recon defaults and returns `VolumesResponse` containing `VolumeObjectDBInfo` objects.

## Control Flow

The endpoint calls `omMetadataManager.listVolumes(prevKey, limit)`, maps each `OmVolumeArgs` into a `VolumeObjectDBInfo`, and returns the result count plus list. IO failures produce HTTP 500.

## State and Persistence

It is read-only and depends on Recon's OM volume table mirror.

## Dependencies and Integration Points

It integrates with `ReconOMMetadataManager`, `OmVolumeArgs`, and volume response DTOs.

## Risks and Edge Cases

Pagination behavior depends on `listVolumes` interpreting `prevKey` consistently with OM DB ordering. Negative or excessive limits rely on upstream/default handling. The endpoint imports `StringUtils` for prevKey defaults and does no readiness check.

## Test Signals

Tests should cover default pagination, explicit `prevKey`, limit boundaries, empty tables, DTO mapping, and IOException response handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/VolumeEndpoint.java -->
