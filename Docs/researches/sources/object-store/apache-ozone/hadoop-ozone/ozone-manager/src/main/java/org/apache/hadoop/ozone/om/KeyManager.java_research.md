# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManager.java

## Purpose

`KeyManager` defines the OM key-level service contract. It extends filesystem-style OM operations through `OzoneManagerFS` and ACL behavior through `IOzoneAcl`.

## Important APIs and Types

The interface covers lifecycle (`start`, `stop`), key lookup/info/listing (`lookupKey`, `getKeyInfo`, `listKeys`), pending deletion queues (`getPendingDeletionKeys`, `getDeletedKeyEntries`, `getDeletedDirEntries`, `getPendingDeletionSubDirs`, `getPendingDeletionSubFiles`), snapshot rename/deletion lookups, previous-snapshot object lookup functions, multipart upload listing and cleanup selection, object tagging, block-location refresh, metadata manager access, and access to background services such as key deleting, directory deleting, open-key cleanup, multipart cleanup, SST filtering, snapshot defrag/deleting, and compaction.

## Control Flow

This file is an interface, so it defines contracts rather than implementation. The default `getDeletedDirEntries()` delegates to `getDeletedDirEntries(null, null)`. The default `getDeletedDirEntries(volume, bucket, size)` opens an iterator, copies up to `size` key/value pairs into a list using `Table.newKeyValue`, closes the iterator with try-with-resources, and returns the list.

## State and Persistence

The interface describes access to OM metadata tables for keys, open keys, deleted keys, deleted directories, multipart uploads, snapshot metadata, and rename entries. Implementations persist and read state through `OMMetadataManager` and related RocksDB-backed tables. Background services exposed by the interface mutate deletion and cleanup state over time.

## Dependencies and Integration Points

It integrates with OM helpers (`OmKeyInfo`, `OmKeyArgs`, `OmBucketInfo`, `OmDirectoryInfo`, multipart list types, `BucketLayout`, `RepeatedOmKeyInfo`), database abstractions (`Table`, `TableIterator`), Ratis/checked functions, Ozone Manager filesystem interface, background service classes, snapshot services, compaction service, and protobuf `ExpiredMultipartUploadsBucket`.

## Risks and Edge Cases

The contract is broad and central, so implementation consistency is critical. Pagination and filtering behavior for deletion queues must avoid starvation. Snapshot previous-object lookup functions return deferred `CheckedFunction<KeyManager,...>` values, which require careful lifecycle and snapshot table handling by callers. Cleanup service getters expose internal background services, so null/lifecycle handling matters during OM startup/shutdown. The default iterator-copy helper returns direct value objects and relies on iterator implementations for ordering and isolation.

## Test Signals

Strong coverage comes from key manager implementation tests for lookup/listing, block refresh, tags, multipart listing/expiration, open key cleanup, deleted key and deleted directory iteration, snapshot-aware deletion/rename logic, background service lifecycle, and ACL behavior inherited from `IOzoneAcl`.
