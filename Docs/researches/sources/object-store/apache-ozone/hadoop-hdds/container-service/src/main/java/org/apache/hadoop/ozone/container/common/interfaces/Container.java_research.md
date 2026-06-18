<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java

Purpose: primary container abstraction for lifecycle, metadata, reports, import/export, scanning, locking, and data movement.

Important APIs and control flow: lifecycle methods create, delete, update, mark for close/delete/unhealthy, quasi-close, close, and update delete transaction/BCSID. Data APIs import/export through `ContainerPacker`, copy directories, expose the `.container` file, and report protobuf replica state. Scan APIs separate metadata scan, data scan eligibility, and throttled/cancelable data scan. Lock APIs expose explicit read/write lock acquisition, interruptible variants, unlock, and ownership checks.

State and persistence: interface only, but implementations are expected to persist metadata updates and lifecycle state to container files and metadata stores. Locking contract is central to safe concurrent writes, scans, and state transitions.

Dependencies and integration: implemented by key-value containers and consumed by `ContainerSet`, `Handler`, `HddsDispatcher`, scanners, import/export tools, and report publishers.

Risks and test signals: implementation tests should cover persistence after every lifecycle transition, force update behavior, lock ownership and interruptibility, scan behavior by state, import/export round trips, and BCSID/delete transaction updates. Callers must know whether methods require caller-held locks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Container.java -->
