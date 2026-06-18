<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Full Hadoop 3 bucket-scoped Ozone filesystem for `o3fs`, adding token issuer, lease recovery, safe mode, storage statistics, and stream capabilities to `BasicOzoneFileSystem`.

## Important APIs, types, and functions
Implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`. It manages `OzoneFSStorageStatistics`, creates `OzoneClientAdapterImpl`, wraps input/output/datastreams in capable wrappers, exposes key provider token issuers, implements `hasPathCapability`, `recoverLease`, `isFileClosed`, and `setSafeMode`.

## Control flow
Construction reads the `FORCE_LEASE_RECOVERY_ENV` system property. `recoverLease` prepares recovery through the adapter, treats `KEY_ALREADY_CLOSED` as success, asks `LeaseRecoveryClientDNHandler` for finalized block lengths, builds `OmKeyArgs` with summed length and recovered locations, and commits recovery through the adapter.

## State and persistence behavior
Local state is statistics and the force-recovery flag. Persistent changes include file recovery commits and safe mode actions through OM; key provider access may include external KMS token issuer integration.

## Dependencies and integration points
Connects Hadoop 3 APIs to Ozone adapters, storage statistics, lease recovery helper, OM lease metadata, encryption key providers, and path capability helper.

## Risks and test signals
Lease recovery can commit incorrect lengths if block recovery data is wrong. `isFileClosed` lacks a storage statistic increment in this Hadoop 3 variant. Tests should cover token issuers, hsync capabilities, recoverLease strict/forced paths, safe mode, and storage statistics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
