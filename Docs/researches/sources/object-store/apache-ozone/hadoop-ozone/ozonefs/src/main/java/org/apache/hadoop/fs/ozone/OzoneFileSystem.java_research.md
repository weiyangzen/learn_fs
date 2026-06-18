<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Main unshaded full `o3fs` filesystem implementation.

## Important APIs, types, and functions
Extends `BasicOzoneFileSystem`, implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`, maintains `OzoneFSStorageStatistics`, creates `OzoneClientAdapterImpl`, wraps streams with capability classes, exposes key provider issuers, path capabilities, lease recovery, file-closed check, and safe mode.

## Control flow
The behavior matches the Hadoop 3 compatibility version: construction reads force-recovery property, recovery prepares OM lease info, handles already-closed keys, finalizes block lengths, builds `OmKeyArgs`, and commits recovery. Stream creation hooks return capable wrappers.

## State and persistence behavior
Local state is statistics and force recovery. Persistent effects include file recovery commits, safe mode toggles, and normal inherited filesystem mutations.

## Dependencies and integration points
This is the main artifact's bridge from Hadoop clients to Ozone adapter, key providers, lease recovery, and storage statistics.

## Risks and test signals
Risks are identical to the Hadoop 3 `o3fs` class, including lease recovery correctness and stats coverage. Tests should compare main and hadoop3 behavior to avoid drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
