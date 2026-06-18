## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerDBDefinition.java

Purpose: Defines the master-volume RocksDB schema that records containers witnessed on a datanode.

Important APIs and functions: Singleton `get()` returns the DB definition. `CONTAINER_CREATE_INFO_TABLE_DEF` maps `ContainerID` keys to `ContainerCreateInfo` values in `ContainerCreateInfoTable`. `getName()` returns the witnessed-container DB name. `getLocationConfigKey()` points to the datanode ID directory configuration. Package-private `getContainerCreateInfoTableDef()` exposes the table definition to the store implementation.

Control flow and state: The class extends `DBDefinition.WithMap` with one immutable column family map and a singleton instance.

Persistence and dependencies: Uses `ContainerID.getCodec()`, `ContainerCreateInfo.getCodec()`, SCM config keys, and `OzoneConsts.WITNESSED_CONTAINER_DB_NAME`. `WitnessedContainerMetadataStoreImpl` opens and reads this definition.

Risks: The location is global to the datanode identity/master volume rather than individual container volumes. Table definition visibility is package-private, so schema changes must be coordinated in the metadata package.

Test signals: DBDefinition name/location resolution, table codec round trip, singleton behavior, opening store through `WitnessedContainerMetadataStoreImpl`, and upgrade compatibility with previous table name.
