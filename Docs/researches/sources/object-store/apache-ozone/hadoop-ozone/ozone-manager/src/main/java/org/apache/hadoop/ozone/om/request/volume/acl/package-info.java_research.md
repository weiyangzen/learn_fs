# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/acl/package-info.java

Purpose: This package documentation identifies the package as the volume ACL request/response area.

Important APIs and types: The package contains the abstract volume ACL request and add/remove/set concrete request implementations.

Control flow: Package flow follows OM request handling: preExecute authorization and normalization, lock-scoped cache mutation, response DB batching, and audit completion.

State and persistence behavior: State changes target `OmVolumeArgs` ACL lists in the volume table.

Dependencies and integration points: It integrates with volume request helpers, ACL authorizer, audit logger, and volume ACL response classes.

Risks and test signals: Package-level tests should cover all three operations and verify no-op versus applied behavior.
