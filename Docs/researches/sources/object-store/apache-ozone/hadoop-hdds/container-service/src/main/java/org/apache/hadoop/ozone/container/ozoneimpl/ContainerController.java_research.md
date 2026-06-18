## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerController.java

Purpose: Acts as the datanode control-plane facade for container lookup, state transitions, reports, import/export/copy/delete, reconciliation, scanner updates, and handler dispatch.

Important APIs and functions: Exposes container lookup/location, close/quasi-close/mark-for-close, `markContainerUnhealthy()`, checksum updates, reports, finalized block recording/checking, import/copy/export/delete, reconciliation, iteration by all containers or volume, volume container counts, and data scan timestamp updates.

Control flow and state: The controller holds a `ContainerSet` and a map from container type to `Handler`. Most operations fetch the container, choose the handler by type, and delegate. Export failures trigger an on-demand container scan through `ContainerSet.scanContainer()` before rethrowing. Missing containers are logged and often treated as skipped except close paths that throw.

Persistence and dependencies: Persistence occurs inside handlers and containers: state files, checksums, data scan timestamps, and container reports. Integrates with `DNContainerOperationClient`, `ContainerMerkleTreeWriter`, `TarContainerPacker`, and HDDS container protobuf/report types.

Risks: `getHandler(container)` assumes non-null container and registered handler. Several methods do not guard null containers before handler calls. Missing-container behavior differs by operation. Export failure scanning is side-effectful. Package-private `updateDataScanTimestamp()` is used by scanner helpers.

Test signals: Handler dispatch for each operation, missing container close versus mark unhealthy/update checksum behavior, export failure scan trigger, finalized block APIs, per-volume iteration/count, reconciliation delegation, and null/unregistered handler failure modes.
