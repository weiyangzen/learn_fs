# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/GlobalStorageReport.java

## Purpose
Global storage aggregate for capacity distribution APIs, summarizing filesystem capacity, reserved space, Ozone capacity, used/free/committed space, and minimum free space.

## Important APIs, Types, And Functions
declares `GlobalStorageReport`, `Builder`; key fields include `totalFileSystemCapacity`, `totalReservedSpace`, `totalOzoneCapacity`, `totalOzoneUsedSpace`, `totalOzoneFreeSpace`, `totalOzoneCommittedSpace`, `totalMinimumFreeSpace`, `totalReservedSpace`, `totalOzoneCapacity`, `totalOzoneUsedSpace`; important methods include `getTotalFileSystemCapacity`, `getTotalReservedSpace`, `getTotalOzoneCapacity`, `getTotalOzoneUsedSpace`, `getTotalOzoneFreeSpace`, `getTotalOzoneCommittedSpace`, `getTotalMinimumFreeSpace`, `newBuilder`, `setTotalReservedSpace`, `setTotalOzoneCapacity`, `setTotalOzoneUsedSpace`, `setTotalOzoneFreeSpace`.

## Control Flow
Builder computes `totalFileSystemCapacity` as reserved plus Ozone capacity and validates all totals are non-negative.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover builder validation, derived filesystem capacity, and large cluster totals.
