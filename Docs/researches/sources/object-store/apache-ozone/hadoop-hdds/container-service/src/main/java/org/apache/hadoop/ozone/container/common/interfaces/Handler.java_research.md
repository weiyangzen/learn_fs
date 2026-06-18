<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java

Purpose: abstract per-container-type command handler used by `HddsDispatcher`.

Important APIs and control flow: the static factory currently maps `KeyValueContainer` to `KeyValueHandler`. The base class stores config, datanode ID, `ContainerSet`, `VolumeSet`, metrics, cluster ID, and ICR sender. `sendICR` and `sendDeferredICR` skip RECOVERING containers and otherwise publish immediate or deferred incremental reports. Abstract methods cover command handling, stream channels, import/export, stop, lifecycle transitions, checksum updates, unhealthy/quasi/closed states, delete, reconcile, delete block/unreferenced data, finalized block tracking, copy, import from temp container data, and streaming block reads.

State and persistence: handlers are responsible for mutating and persisting container state, metadata, checksum files, block deletes, and ICR side effects. The base class only holds references and cluster ID.

Dependencies and integration: central integration point between dispatcher and concrete key-value container implementation. Depends on checksum managers, Ratis data channels, tar packer, report sender, volume set, metrics, and operation clients.

Risks and test signals: handler implementations require broad tests for each command type, ICR behavior, RECOVERING skip, checksum update atomicity, delete safety, reconciliation, and stream reads/writes. Adding a new container type requires extending the factory and likely the YAML/layout utilities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/Handler.java -->
