# sources/storage-engines/foundationdb/fdbcli/HotRangeCommand.cpp

Purpose: Implements `hotrange`, a storage-server diagnostic command that queries read hot-range metrics from one selected storage server and prints JSON ranges with metrics.

Important APIs/types/functions: `hotRangeCommandActor(Database localdb, Reference<IDatabase> db, tokens, storage_interface)`, private `parseSplitType`, `getStorageServerInterfaces`, `ReadHotSubRangeRequest::SplitType`, `ReadHotRangeWithMetrics`, and `localdb->getHotRangeMetrics`.

Control flow: With no arguments, the command refreshes the caller-owned `storage_interface` map and prints queryable storage server addresses. With exactly six tokens, it requires a non-empty cache, validates the address exists, parses `splitCount` with `boost::lexical_cast<int>`, maps split type from `bytes`, `readBytes`, or `readOps` with fallback to bytes for unknown strings, builds a key range from begin/end tokens, queries hot range metrics through the native local database, and serializes each metric object to pretty JSON. Other token counts print usage.

State and persistence behavior: Read-only against storage-server metrics. The only state is transient cached storage interfaces maintained outside this actor.

Dependencies and integration points: Depends on fdbcli utility discovery of storage interfaces, storage-server metric RPCs, JSON output, and native database access because the code notes multiversion support is not yet refactored.

Risks: Requires a prior cache-populating invocation; stale cache can reject valid servers or target old interfaces. Unknown split type logs an error but still runs with bytes, which may surprise users. It does not validate `begin < end` or `splitCount > 0` locally.

Test signals: Cover listing, empty/stale cache handling, split type parsing, invalid split count, unknown split type fallback, JSON output shape, range validation expectations, and storage-server RPC errors.
