<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java

## Purpose

`ContainerLogger` writes compact, long-retention container replica event records to the dedicated Log4j logger named `ContainerLog`. It captures successful state changes, import/export/recovery/reconcile/move events, and failure events without flooding the main datanode log. The complete 218-line file was read.

## Important APIs, Types, and Functions

Public static log methods include `logOpen`, `logClosing`, `logQuasiClosed`, `logClosed`, `logUnhealthy`, `logLost`, `logDeleted`, `logImported`, `logExported`, `logRecovered`, `logChecksumUpdated`, `logReconciled`, and `logMoveSuccess`. Private `getMessage` overloads build pipe-separated fields.

## Control Flow

Each public method formats a container message after the related event succeeds and logs at info, warn, or error level depending on severity. Base fields are container ID, replica index, BCSID, state, volume, and data checksum. Specialized methods append reasons, old/new checksums, peer details, move source/destination, size, and elapsed time.

## State and Persistence Behavior

No Java state is persisted by the class. Persistence is the configured Log4j appender for `ContainerLog`.

## Dependencies and Integration Points

It depends on `ContainerData`, `ScanResult`, `DatanodeDetails`, `StorageVolume`, Log4j, and `HddsUtils.checksumToString`. It is intended for container lifecycle code paths after successful transitions.

## Risks and Edge Cases

Logging before an operation succeeds would produce misleading history; the class documentation explicitly warns against that. Peer `toString()` and volume `toString()` content affect log stability. Multi-field message formatting uses `" | "`, so appended fields should avoid ambiguous embedded separators when possible.

## Test Signals

Tests should verify formatting fields, log levels for each event class, checksum update/reconcile messages, move-success details, and that lifecycle callers invoke these methods only after successful state changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/ContainerLogger.java -->
