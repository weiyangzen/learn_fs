# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DeletedBlockLog.java

Purpose: Contract for SCM's persisted log of blocks pending physical deletion on datanodes.

Important APIs and types: Defines `getTransactions`, `incrementCount`, `recordTransactionCreated`, `onDatanodeDead`, `onSent`, `addTransactions`, `getNumOfValidTransactions`, `reinitialize`, `getTransactionToDNsCommitMapSize`, and `getTransactionSummary`.

Control flow: Producers add deletion transactions. The background service scans transactions, records command creation and send state, increments retry counts, and implementations process ACKs/status changes.

State and persistence behavior: Implementations persist `DeletedBlocksTransaction` records and support reinitialization from SCM metadata tables.

Dependencies and integration points: Central interface between `BlockManagerImpl`, `SCMBlockDeletingService`, SCM HA metadata, and datanode command status handling.

Risks: Duplicate suppression, retry handling, and removal must survive leadership changes and datanode failures. Add semantics must be atomic.

Test signals: Cover add/scan/remove, reinitialize, datanode death, command status flows, summary counters, and map-size throttling.
