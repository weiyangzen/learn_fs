## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanError.java

Purpose: Captures a specific scanner-detected container health error with failure type, affected file, and exception.

Important APIs and functions: `FailureType` enumerates missing directories/files, corrupt metadata/chunks, missing or inconsistent data files, inaccessible DB, and write failure. Constructor stores failure, file, and exception. Getters expose fields and `toString()` formats the error.

Control flow and state: Immutable after construction, except the referenced exception object may be mutable. Used inside `MetadataScanResult` and `DataScanResult` error lists.

Persistence and dependencies: No persistence. Errors are consumed by scanner helpers and container state handlers to mark containers unhealthy and log details.

Risks: Failure type granularity drives operational response; missing a category can force generic handling. The constructor accepts `Exception` but field type is `Throwable`, so callers with non-Exception throwables cannot pass them without wrapping. `toString()` may include verbose exception text.

Test signals: Construct each failure type, verify getters/toString, propagate through metadata/data scan results, and ensure scanner helper logs and unhealthy marking include error details.
