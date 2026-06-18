# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/package-info.java

## Purpose

This package descriptor marks `org.apache.hadoop.ozone.common` as the home for common HDDS/Ozone classes. In this work item the package contains chunk-buffer abstractions, checksum exception types, CRC helpers, and storage-state exceptions.

## APIs and integration

There are no executable APIs. The JavaDoc package comment is consumed by generated documentation and by developers navigating the module. It anchors shared code that is used by container helpers, checksum code, and replication/serialization paths.

## State, dependencies, risks, and test signals

The file has no state, persistence, or runtime dependencies. The only risk is documentation drift if the package's role changes. Tests are not needed for this file, but documentation checks can ensure package descriptors remain valid and compile with JavaDoc.
