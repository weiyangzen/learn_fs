# sources/storage-engines/pebble/data_test.go

Purpose: Shared datadriven command harness for Pebble tests. In this subset it supports DB state definition, SST construction, compaction execution, iteration, ingestion, excision, metadata/layout inspection, option parsing, and value-separation fixture setup.

Important APIs/types/functions: Core helpers include `runGetCmd`, `runIterCmd`, `parseIterOptions`, `printIterState`, `runBatchDefineCmd`, `runBuildCmd`, `runBuildSSTCmd`, `runBuildRemoteCmd`, `runDBDefineCmd`, `runCompactCmdFn`, `runCompactCmd`, `runWaitForTableStatsCmd`, `runTableFileSizesCmd`, `runVersionFileSizes`, `runSSTablePropertiesCmd`, `runLayoutCmd`, `runPopulateCmd`, `runExciseCmd`, `runIngestAndExciseCmd`, `runIngestCmd`, `runIngestExternalCmd`, `runLSMCmd`, `describeLSM`, `parseDBOptionsArgs`, and `defineDBValueSeparator`.

Control flow: Helpers parse datadriven commands and convert textual keys, spans, values, options, and file specs into DB operations. `runDBDefineCmd` is the most complex path: it opens a DB, creates memtables/SSTables for declared levels, simulates flush compactions, rewrites version edits to requested levels, ratchets sequence numbers, fabricates blob metadata, applies the edit, updates read state, and waits for table stats.

State and persistence: Usually uses in-memory VFS/remote storage but creates real table/blob objects there. It mutates DB internals under lock, including versions, memtable queues, snapshots, table stats flags, sequence numbers, and span policy functions. `defineDBValueSeparator` accumulates blob metadata and values for readable blob-reference fixtures.

Dependencies and integration: Integrates with `datadriven`, `crstrings`, `manifest`, `keyspan`, `rangekey`, `sstable`, `objstorage`, `remote`, `blobtest`, `valsep`, `wal`, `errorfs`, and test key utilities. Many compaction tests depend on these helpers.

Risks: The harness intentionally permits invalid states, so helper misuse can bypass production invariants. Direct internal mutation must track production refactors. Broad string parsing must remain backward-compatible with many fixtures. Async table stats require explicit waits.

Test signals: Enables high-signal golden tests for iteration, compaction, ingestion, table stats, value separation, external files, virtual tables, excision, and option parsing.
