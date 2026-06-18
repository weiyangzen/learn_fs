## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/MetadataScanResult.java

Purpose: Represents the result of a container metadata scan, including errors or a deleted-container signal.

Important APIs and functions: `fromErrors()` returns an interned healthy result for empty error lists or a new error result. `deleted()` returns an interned deleted result. `isDeleted()`, `hasErrors()`, and `getErrors()` implement `ScanResult`. `toString()` summarizes healthy, deleted, single-error, and multi-error states.

Control flow and state: Immutable fields hold the error list reference and deleted flag. Common healthy and deleted cases are static singletons.

Persistence and dependencies: No persistence. Consumed by `ContainerScanHelper` to decide unhealthy marking and by `DataScanResult.unhealthyMetadata()` when data scans abort early.

Risks: The constructor stores the list reference without copying; callers should provide immutable or stable lists. A deleted result has no errors and is handled separately from healthy. `toString()` only includes the first error for multi-error summaries.

Test signals: Empty and non-empty error lists, deleted result, immutable list expectations, `ScanResult` contract, toString variants, and scanner helper branching on deleted/errors.
