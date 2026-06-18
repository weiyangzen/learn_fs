## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconSCMDBDefinition.java

Purpose: `ReconSCMDBDefinition` defines Recon's SCM RocksDB schema by extending SCM's DB schema with a Recon-specific node table and database name/location.

Important APIs and types: declares `RECON_SCM_DB_NAME`, `NODES`, `DATANODE_ID_CODEC`, `COLUMN_FAMILIES`, singleton `get`, `getName`, and `getLocationConfigKey`. `NODES` maps `DatanodeID` to `DatanodeDetails`.

Control flow: callers use `ReconSCMDBDefinition.get()` when creating/opening DB stores. The definition combines `SCMDBDefinition.get().getMap()` with `NODES`, so inherited SCM tables and Recon's node table are available from one DB.

State and persistence: defines persisted column families, not runtime state. The DB name is `recon-scm.db`; location is controlled by `OZONE_RECON_SCM_DB_DIR`.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade` to create and reopen DB stores, by `ReconNodeManager` for nodes, by `ReconContainerManager` for node lookups and containers, by `ReconPipelineManager` for pipelines, and by `SequenceIdGenerator`.

Risks and edge cases: schema compatibility depends on upstream `SCMDBDefinition`; adding the `NODES` table must not collide with upstream column family names. `DelegatedCodec` stores `DatanodeID` as UUID string; any format drift affects old DB reads.

Test signals: SCM facade tests indirectly exercise DB creation. Dedicated schema tests should assert all inherited SCM tables plus `nodes` are present and that DB location/name are Recon-specific.
