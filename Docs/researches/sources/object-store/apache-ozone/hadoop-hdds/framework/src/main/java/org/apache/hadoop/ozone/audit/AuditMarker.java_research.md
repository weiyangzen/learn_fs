# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMarker.java

## Purpose

`AuditMarker` defines log4j2 markers used to classify audit events. The complete 41-line source was read for this report.

## Important APIs, Types, and Functions

Constants are `WRITE`, `READ`, `AUTH`, and `PERFORMANCE`, each created through `MarkerManager.getMarker`. `getMarker()` returns the log4j2 marker.

## Control Flow

Enum construction creates markers once; `AuditLogger` attaches them to log calls.

## State and Persistence Behavior

Markers are in-memory log metadata that influence log4j2 filtering and routing.

## Dependencies and Integration Points

It depends on log4j2 `Marker` and `MarkerManager`, and integrates with log4j2 audit configuration.

## Risks and Edge Cases

Marker name changes would break marker-based filters and audit routing.

## Test Signals

Tests should verify logger methods use expected markers and log4j2 sample configurations filter each marker type correctly.
