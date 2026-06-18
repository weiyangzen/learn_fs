## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStore.java

Purpose: Defines typed access to the witnessed-container metadata DB in the datanode master volume.

Important APIs and functions: Extends `DBStoreManager` and adds `getContainerCreateInfoTable()`, returning a table of `ContainerID` to `ContainerCreateInfo`.

Control flow and state: This is an interface. Implementations can choose the current protobuf-valued table or a previous-version compatibility table depending on upgrade finalization state.

Persistence and dependencies: The table is used by container loading to remember the last loaded container creation state and EC replica index. It depends on HDDS `Table` and SCM `ContainerID`.

Risks: Callers must use the interface instead of assuming a specific physical table, because upgrades can route to a legacy string-valued table. Incorrect witnessed metadata can cause EC container loads to be ignored.

Test signals: Compile users, access table before and after upgrade finalization, write/read `ContainerCreateInfo`, and validate `ContainerReader` behavior when DB replica index differs from on-disk container replica index.
