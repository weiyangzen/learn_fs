## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/ContainerTestUtils.java

Purpose: `ContainerTestUtils` is a broad test utility class for constructing datanode endpoints, containers, handlers, dispatchers, scan results, layouts, Ratis servers, and block metadata.

Important APIs and functions: major helpers include `createEndpoint`, `getOzoneContainer`, `getMockContext`, `createDatanodeDetails`, `getContainer`, overloaded `getKeyValueHandler`, `getHddsDispatcher`, schema V3 toggles, `createDbInstancesForTestIfNeeded`, `setupMockContainer`, healthy/unhealthy scan result builders, `addContainerToDeletedDir`, `addContainerToVolumeDir`, `getNoopContainerDispatcher`, `getEmptyContainerController`, `newXceiverServerRatis`, `initializeDatanodeLayout`, and `createBlockMetaData`.

Control flow and state: endpoint creation configures protobuf RPC and wraps a proxy in `StorageContainerDatanodeProtocolClientSideTranslatorPB`. Container helpers create realistic `KeyValueContainerData`, choose volumes, create and close containers, or move them to deleted dirs. Mock helpers stub scan and context behavior. Metadata creation writes block rows and checksum-bearing chunks into the container DB.

Persistence and integration: utilities create real volume directories, initialize layout storage, create container DB entries, and can construct live RPC clients and Ratis servers. They integrate with most container-service subsystems.

Risks and test signals: because this utility is broad, changes have large test blast radius. Static shared no-op dispatcher and empty controller are safe only for tests that do not need real dispatch behavior. Schema V3 DB initialization mirrors production volume checks and is important for compatibility tests.
