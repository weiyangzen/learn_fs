<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java

Purpose: common result contract for container scan outcomes.

Important APIs and control flow: exposes `hasErrors`, `isDeleted`, and `getErrors`, where errors are `ContainerScanError` entries.

State and persistence: interface only. Implementations represent scan outcome state and may be used to drive persistent lifecycle transitions such as marking containers unhealthy or deleted.

Dependencies and integration: consumed by `Handler.markContainerUnhealthy` and implemented by metadata/data scan result classes in `ozoneimpl`.

Risks and test signals: scan result implementations should be tested for deleted-without-errors, errors-with-deleted, immutable error lists, and correct translation into handler state changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ScanResult.java -->
