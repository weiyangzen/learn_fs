# Folder Research: sources/storage-engines/foundationdb/fdbclient

This folder summary is inferred from accepted per-file research outputs.

- Direct researched files: 89
- Recursive researched files: 213
- Direct child folders represented: 5

## Direct Files

- `sources/storage-engines/foundationdb/fdbclient/ActorLineageProfiler.cpp`
- `sources/storage-engines/foundationdb/fdbclient/AnnotateActor.cpp`
- `sources/storage-engines/foundationdb/fdbclient/AsyncFileBlobStore.cpp`
- `sources/storage-engines/foundationdb/fdbclient/Atomic.cpp`
- `sources/storage-engines/foundationdb/fdbclient/AuditUtils.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupAgentBase.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainer.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.h`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainerFileSystem.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.h`
- `sources/storage-engines/foundationdb/fdbclient/BackupTLSConfig.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BlobStoreCommon.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BuildFlags.h.in`
- `sources/storage-engines/foundationdb/fdbclient/BulkDumping.cpp`
- `sources/storage-engines/foundationdb/fdbclient/BulkLoading.cpp`
- `sources/storage-engines/foundationdb/fdbclient/CMakeLists.txt`
- `sources/storage-engines/foundationdb/fdbclient/ClientKnobs.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ClientStatusReport.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ClusterConnectionFile.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.h`
- `sources/storage-engines/foundationdb/fdbclient/ClusterConnectionMemoryRecord.cpp`
- `sources/storage-engines/foundationdb/fdbclient/CommitProxyInterface.cpp`
- `sources/storage-engines/foundationdb/fdbclient/CoordinationInterface.cpp`
- `sources/storage-engines/foundationdb/fdbclient/DataDistributionConfig.cpp`
- `sources/storage-engines/foundationdb/fdbclient/DatabaseBackupAgent.cpp`
- `sources/storage-engines/foundationdb/fdbclient/DatabaseConfiguration.cpp`
- `sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h`
- `sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FluentDSampleIngestor.cpp`
- `sources/storage-engines/foundationdb/fdbclient/GCSBlobStore.cpp`
- `sources/storage-engines/foundationdb/fdbclient/GCSBlobStore.h`
- `sources/storage-engines/foundationdb/fdbclient/GlobalConfig.cpp`
- `sources/storage-engines/foundationdb/fdbclient/IdempotencyId.cpp`
- `sources/storage-engines/foundationdb/fdbclient/JsonBuilder.cpp`
- `sources/storage-engines/foundationdb/fdbclient/KeyRangeMap.cpp`
- `sources/storage-engines/foundationdb/fdbclient/KnobValue.cpp`
- `sources/storage-engines/foundationdb/fdbclient/LinkTest.cpp`
- `sources/storage-engines/foundationdb/fdbclient/LocalClientAPI.cpp`
- `sources/storage-engines/foundationdb/fdbclient/LocalClientAPI.h`
- `sources/storage-engines/foundationdb/fdbclient/ManagementAPI.cpp`
- `sources/storage-engines/foundationdb/fdbclient/MonitorLeader.cpp`
- `sources/storage-engines/foundationdb/fdbclient/MultiVersionTransaction.cpp`
- `sources/storage-engines/foundationdb/fdbclient/MutationLogReader.cpp`
- `sources/storage-engines/foundationdb/fdbclient/NameLineage.cpp`
- `sources/storage-engines/foundationdb/fdbclient/NameLineage.h`
- `sources/storage-engines/foundationdb/fdbclient/NativeAPI.actor.cpp`
- `sources/storage-engines/foundationdb/fdbclient/PartitionedLogIterator.h`
- `sources/storage-engines/foundationdb/fdbclient/Printable.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ProxyLoadBalance.h`
- `sources/storage-engines/foundationdb/fdbclient/RESTClient.cpp`
- `sources/storage-engines/foundationdb/fdbclient/RESTClient.h`
- `sources/storage-engines/foundationdb/fdbclient/RESTUtils.cpp`
- `sources/storage-engines/foundationdb/fdbclient/RESTUtils.h`
- `sources/storage-engines/foundationdb/fdbclient/RYWIterator.cpp`
- `sources/storage-engines/foundationdb/fdbclient/RandomKeyValueUtils.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ReadYourWrites.actor.cpp`
- `sources/storage-engines/foundationdb/fdbclient/RestoreInterface.cpp`
- `sources/storage-engines/foundationdb/fdbclient/RestoreInterface.h`
- `sources/storage-engines/foundationdb/fdbclient/S3BlobStore.cpp`
- `sources/storage-engines/foundationdb/fdbclient/S3Client.cpp`
- `sources/storage-engines/foundationdb/fdbclient/S3Client_cli.cpp`
- `sources/storage-engines/foundationdb/fdbclient/Schemas.cpp`
- `sources/storage-engines/foundationdb/fdbclient/SpecialKeySpace.cpp`
- `sources/storage-engines/foundationdb/fdbclient/StackLineage.cpp`
- `sources/storage-engines/foundationdb/fdbclient/StatusClient.cpp`
- `sources/storage-engines/foundationdb/fdbclient/StorageCheckpoint.cpp`
- `sources/storage-engines/foundationdb/fdbclient/StorageServerInterface.cpp`
- `sources/storage-engines/foundationdb/fdbclient/Subspace.cpp`
- `sources/storage-engines/foundationdb/fdbclient/SystemData.cpp`
- `sources/storage-engines/foundationdb/fdbclient/TagThrottle.cpp`
- `sources/storage-engines/foundationdb/fdbclient/TaskBucket.cpp`
- `sources/storage-engines/foundationdb/fdbclient/ThreadSafeTransaction.cpp`
- `sources/storage-engines/foundationdb/fdbclient/Tracing.cpp`
- `sources/storage-engines/foundationdb/fdbclient/TransactionLineage.cpp`
- `sources/storage-engines/foundationdb/fdbclient/Tuple.cpp`
- `sources/storage-engines/foundationdb/fdbclient/TupleVersionstamp.cpp`
- `sources/storage-engines/foundationdb/fdbclient/VersionVector.cpp`
- `sources/storage-engines/foundationdb/fdbclient/WriteMap.cpp`
- `sources/storage-engines/foundationdb/fdbclient/azurestorage.cmake`
- `sources/storage-engines/foundationdb/fdbclient/fdbclient_test.cpp`
- `sources/storage-engines/foundationdb/fdbclient/notified_support.swift`
- `sources/storage-engines/foundationdb/fdbclient/versions.h.cmake`
- `sources/storage-engines/foundationdb/fdbclient/zipf.c`

## Research Role

This directory participates in subset B filesystem research through the listed source files.
