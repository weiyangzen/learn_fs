<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Full Hadoop 3 rooted OFS implementation with encryption token issuer support, lease recovery, safe mode, storage statistics, and stream capabilities.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem` and implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`. It creates `RootedOzoneClientAdapterImpl`, wraps streams in capable wrappers, exposes key provider APIs, reports storage statistics, implements path capabilities, `recoverLease`, `isFileClosed`, and `setSafeMode`.

## Control flow
Recovery mirrors the bucket-scoped filesystem: prepare with adapter, return success if already closed, finalize block lengths through `LeaseRecoveryClientDNHandler`, build `OmKeyArgs`, then call `recoverFile`. `isFileClosed` qualifies the path and delegates to the adapter.

## State and persistence behavior
Local state is the storage statistics object and force-recovery flag. Persistent mutations occur through recovery commits and safe-mode requests to OM.

## Dependencies and integration points
Integrates rooted path translation from the base filesystem with Hadoop 3 token issuer and lease recovery APIs. It uses `RootedOzoneClientAdapterImpl`, `OzonePathCapabilities`, and the common lease-recovery helper.

## Risks and test signals
Risk mirrors `OzoneFileSystem` with additional rooted path complexity. This variant increments read operations for `isFileClosed`, unlike the `o3fs` Hadoop 3 class. Tests should cover OFS recovery paths, capability probing, stats, and key-provider token issuers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
