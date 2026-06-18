# sources/storage-engines/foundationdb/fdbserver/workloads/FileSystem.cpp

Purpose: Models a file metadata workload with indexed paths, users, servers, deletion state, modification queries, deletion-count queries, and optional concurrent writes.

Important APIs/types/functions: `FileSystemWorkload`, `FileSystemOp`, `RecentModificationQuery`, `ServerDeletionCountQuery`, `initializeFile`, `nodeSetup`, `operationClient`, `writeClient`, `modificationQuery`, `deletionQuery`, `DDSketch`, and formatted key helpers.

Control flow: Setup partitions file IDs across clients, shuffles batches, and initializes metadata plus secondary indexes. Start warms the selected query briefly, resets counters, optionally launches write actors, then launches query actors paced by Poisson delays. Query mode is either recent modifications by user using reverse key selectors or deletion counts by server scanning index pages. Writers randomly toggle deletion state or update file size and last-updated time.

State and persistence behavior: Persistent keys include `/files/id/<id>` metadata, `/size`, `/server`, `/deleted`, `/created`, `/lastupdated`, `/userid`, user updated/path indexes, server deleted index, and global path index. Runtime state tracks query/write counters and latency sketches. Deletion toggles maintain server deleted index entries.

Dependencies/integration: Uses Native API transactions, deterministic random metadata generation, key-selector range reads, Poisson pacing, and DDSketch percentile metrics.

Risks: Some metadata writes duplicate `/server` intentionally/accidentally. User modification indexes are only created during initialization; write updates change `lastupdated` but do not update the user updated index, limiting realism. Query operation object is shared by concurrent actors but stateless.

Test signals: `FileSetupOK`, optional query traces, operations/sec, writes/sec, read latency percentiles, and median write latency.
