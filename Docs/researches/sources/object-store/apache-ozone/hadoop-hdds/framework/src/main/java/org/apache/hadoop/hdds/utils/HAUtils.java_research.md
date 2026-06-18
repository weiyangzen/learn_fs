# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HAUtils.java

## Purpose
`HAUtils` is a stateless helper class used by SCM and OM high-availability paths. It builds SCM protocol clients, reads transaction state from RocksDB checkpoints, replaces local DB directories with downloaded checkpoints, scans existing SST files for incremental snapshot transfer, and fetches SCM CA certificates in HA deployments.

## Important APIs and Types
The main client APIs are `getScmInfo`, `addSCM`, `getScmBlockClient`, and the three `getScmContainerClient` variants. DB/checkpoint APIs include `replaceDBWithCheckpoint`, `getTrxnInfoFromCheckpoint`, `getTransactionInfoTable`, `verifyTransactionInfo`, `getExistingFiles`, and `getExistingSstFilesRelativeToDbDir`. Certificate bootstrapping is handled by `buildCAX509List`, backed by `getCAListWithRetry` and `waitForCACerts`.

## Control Flow and State
SCM calls construct failover proxy providers and wrap translators with `TracingUtil`. `getScmInfo` adjusts retry count based on a configured wait duration before asking the block client for SCM info. Checkpoint installation first moves the old DB aside, creates a transient marker, copies the candidate checkpoint into the live DB path, then deletes the marker. On copy failure it deletes the partial live DB, moves the backup back, and terminates if rollback fails.

## Persistence, Dependencies, and Integration
The class depends on Ozone configuration keys, SCM proxy providers, Ratis retry utilities, Hadoop `FileUtil`, Ratis `FileUtils`, `DBStoreBuilder`, `DBDefinition`, and `TransactionInfo`. It integrates with HA bootstrapping, snapshot installation, OM/SCM metadata DB layouts, and SCM security certificate retrieval.

## Risks and Test Signals
`getTransactionInfoTable` assumes exactly one column family has `TransactionInfo` value type and calls `findFirst().get()`, so malformed DB definitions fail abruptly. `replaceDBWithCheckpoint` protects startup with `DB_TRANSIENT_MARKER`, but copy semantics mean partial directories must be cleaned reliably. CA-list retry intentionally fails fast on `AccessControlException`; tests should cover retry, auth-failure, leader checkpoint index regression, rollback failure, and SST path scanning for nested snapshot directories.
