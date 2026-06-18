# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerHealthState.java

## Purpose
Validates the `ContainerHealthState` enum contract, including individual and combined health states, numeric values, descriptions, and metric names.

## Important APIs, types, and functions
- Exercises enum constants such as under-replicated, over-replicated, mis-replicated, missing, unhealthy, empty, open-unhealthy, quasi-closed-stuck, and open-without-pipeline states.
- Tests `getValue`, `getDescription`, `getMetricName`, and `fromValue` style lookup behavior.
- Includes uniqueness, count, and gap checks for individual and combination value ranges.

## Control flow
The suite asserts explicit values and strings for each enum constant, verifies lookup from numeric values, and scans all enum values for uniqueness and contiguous ranges.

## State and persistence behavior
The file is pure enum contract testing. No persistence or mutable shared state is involved.

## Dependencies and integration points
Container health states feed replication manager reports, SCM metrics, JSON/protobuf serialization, and operational dashboards.

## Risks and test signals
Changing enum numeric values or names can break persisted reports, metrics, and compatibility. These tests are strong compatibility signals for state encoding and observability labels.
