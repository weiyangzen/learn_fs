# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/package-info.java

Purpose: This package documentation marks the package as containing volume request classes.

Important APIs and types: The package includes volume create, delete, owner, quota, quota repair, and shared volume request helper classes.

Control flow: Classes generally use `preExecute` for ACL/time/user normalization and `validateAndUpdateCache` for lock-protected cache mutation.

State and persistence behavior: State changes are staged in OM metadata caches and persisted by paired response classes.

Dependencies and integration points: The package integrates with OM locks, audit, metrics, metadata tables, and protobuf volume RPCs.

Risks and test signals: Broad tests should assert lock ordering, metrics/audit behavior, and source-table-aligned response persistence for every mutation type.
