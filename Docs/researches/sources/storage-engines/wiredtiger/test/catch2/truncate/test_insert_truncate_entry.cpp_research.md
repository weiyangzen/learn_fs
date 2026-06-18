# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp

Purpose: Integration-style Catch2 tests for follower layered-table truncate insertion through `__wt_insert_truncate_entry`.

Important fixtures/APIs: `follower_connection` opens a real disaggregated follower connection with PALite page log, creates `layered:test_truncate_list`, opens a layered cursor, begins a transaction, exposes `WT_LAYERED_TABLE`, and cleans transaction ops in its destructor. Helpers insert one or many entries and create GC-eligible committed entries.

Control flow: scenarios verify insertion returns 0, creates exactly one list entry, increments the layered table dhandle reference only when transitioning from empty to non-empty, preserves `session->dhandle`, stores start/stop keys and layered table pointer, preserves insertion order, registers `WT_TXN_OP_FOLLOWER_TRUNCATE`, allows duplicate ranges, stamps `txn_id`, leaves timestamps unset until commit, releases the truncate lock, and triggers garbage collection of an eligible old entry.

State and persistence: real WiredTiger home `WT_TEST.truncate_list`, layered table metadata, transaction op array, truncate queue, dhandle references, and ingest btree prune timestamp are mutated. No committed user data is the focus; the list state is.

Dependencies/integration: depends on PALite extension, disaggregated follower configuration, layered cursor layout, transaction op cleanup, and truncate GC. Risks include extension availability and internal casts. Test signals are list size/order, refs, txn op contents, timestamps, and lock release.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_insert_truncate_entry.cpp -->
