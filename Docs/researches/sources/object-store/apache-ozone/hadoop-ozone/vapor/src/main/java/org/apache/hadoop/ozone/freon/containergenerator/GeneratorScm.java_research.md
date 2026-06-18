# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorScm.java

Purpose: offline generator for Storage Container Manager metadata rows.

Important APIs/types/functions: command `cgscm`; `call` opens the SCM DB and container table; `writeScmData` writes one `ContainerInfo` per requested index.

Control flow: Freon initialization creates Ozone config and SCM DBStore, gets `SCMDBDefinition.CONTAINERS`, times `writeScmData`, then closes DB. `writeScmData` adds `getContainerIdOffset() + index` as a closed standalone replication-factor-three container owned by `BaseGenerator.getUserId()`.

State/persistence: directly writes SCM RocksDB container metadata. No pipeline, replica, or datanode placement rows are written in this file.

Dependencies/integration: HDDS SCM DB definitions, `ContainerID`, `ContainerInfo`, standalone replication config, Freon metrics, and Vapor service registration.

Risks: must be run offline against a compatible SCM DB. It creates minimal closed container metadata, so other SCM subsystems may require separately generated datanode/OM state to be consistent. Existing container IDs can be overwritten depending on table semantics.

Test signals: no direct test. Integration validation should reopen SCM DB and verify generated `ContainerInfo` state/owner/replication fields.
